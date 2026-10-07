import cgi
import hashlib
import io
import json
import mimetypes
import os
import secrets
import urllib.parse
import zipfile
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "fileshare_storage"
METADATA_DIR = STORAGE_DIR / "metadata"
FILES_DIR = STORAGE_DIR / "files"

MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024
MAX_FILES_PER_SHARE = 100


def ensure_storage():
    STORAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    METADATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    FILES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def parse_args(req):
    args = getattr(
        req,
        "args",
        ""
    )

    if isinstance(args, dict):
        return {
            str(key): str(value)
            for key, value in args.items()
        }

    parsed = urllib.parse.parse_qs(
        str(args),
        keep_blank_values=True
    )

    return {
        key: values[-1]
        for key, values in parsed.items()
    }


def json_body(data):
    return json.dumps(
        data,
        ensure_ascii=False
    )


def error_body(
    message
):
    return json_body(
        {
            "error": message
        }
    )


def html_body(
    body
):
    return body


def generate_share_id():
    while True:
        share_id = secrets.token_urlsafe(9)

        if not metadata_path(
            share_id
        ).exists():
            return share_id


def metadata_path(
    share_id
):
    return (
        METADATA_DIR
        / f"{share_id}.json"
    )


def share_file_directory(
    share_id
):
    return (
        FILES_DIR
        / share_id
    )


def valid_share_id(
    share_id
):
    if not share_id:
        return False

    if len(share_id) > 64:
        return False

    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789-_"
    )

    return all(
        character in allowed
        for character in share_id
    )


def valid_file_id(
    file_id
):
    return valid_share_id(
        file_id
    )


def load_metadata(
    share_id
):
    if not valid_share_id(
        share_id
    ):
        return None

    path = metadata_path(
        share_id
    )

    if not path.is_file():
        return None

    try:
        with path.open(
            "r",
            encoding="utf-8"
        ) as file_handle:
            return json.load(
                file_handle
            )

    except (
        OSError,
        ValueError,
        json.JSONDecodeError
    ):
        return None


def save_metadata(
    share_id,
    metadata
):
    path = metadata_path(
        share_id
    )

    temporary_path = (
        path.with_suffix(".tmp")
    )

    with temporary_path.open(
        "w",
        encoding="utf-8"
    ) as file_handle:
        json.dump(
            metadata,
            file_handle,
            ensure_ascii=False,
            indent=4
        )

    temporary_path.replace(
        path
    )


def create_share():
    ensure_storage()

    share_id = generate_share_id()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    metadata = {
        "id": share_id,
        "created": now,
        "files": []
    }

    share_directory = (
        share_file_directory(
            share_id
        )
    )

    share_directory.mkdir(
        parents=True,
        exist_ok=False
    )

    save_metadata(
        share_id,
        metadata
    )

    return metadata


def get_share(
    share_id
):
    return load_metadata(
        share_id
    )


def get_file_metadata(
    metadata,
    file_id
):
    for file_info in metadata.get(
        "files",
        []
    ):
        if file_info.get(
            "id"
        ) == file_id:
            return file_info

    return None


def calculate_file_id(
    share_id,
    original_name,
    size
):
    value = (
        f"{share_id}:"
        f"{original_name}:"
        f"{size}:"
        f"{secrets.token_hex(16)}"
    )

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()[:24]


def safe_filename(
    filename
):
    filename = Path(
        str(filename)
    ).name

    filename = filename.replace(
        "\x00",
        ""
    )

    if not filename:
        filename = "file"

    return filename[:255]


def save_uploaded_file(
    share_id,
    uploaded_file,
    original_name,
    file_size
):
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            "File is too large."
        )

    share_directory = (
        share_file_directory(
            share_id
        )
    )

    share_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    file_id = calculate_file_id(
        share_id,
        original_name,
        file_size
    )

    destination = (
        share_directory
        / file_id
    )

    temporary_path = (
        share_directory
        / f".{file_id}.upload"
    )

    written = 0

    try:
        with temporary_path.open(
            "wb"
        ) as output:

            while True:
                chunk = uploaded_file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                written += len(
                    chunk
                )

                if written > MAX_FILE_SIZE:
                    raise ValueError(
                        "File is too large."
                    )

                output.write(
                    chunk
                )

        temporary_path.replace(
            destination
        )

    except Exception:
        try:
            temporary_path.unlink()
        except OSError:
            pass

        raise

    return {
        "id": file_id,
        "name": safe_filename(
            original_name
        ),
        "size": written,
        "date": datetime.now(
            timezone.utc
        ).isoformat()
    }


def get_multipart_file():
    content_type = os.environ.get(
        "CONTENT_TYPE",
        ""
    )

    if not content_type.lower().startswith(
        "multipart/form-data"
    ):
        return None

    form = cgi.FieldStorage(
        fp=getattr(
            __import__("sys"),
            "stdin",
            None
        ),
        environ=os.environ,
        keep_blank_values=True
    )

    if "file" not in form:
        return None

    field = form["file"]

    if isinstance(
        field,
        list
    ):
        field = field[0]

    if not getattr(
        field,
        "file",
        None
    ):
        return None

    filename = getattr(
        field,
        "filename",
        None
    )

    if not filename:
        return None

    return field


def handle_create():
    metadata = create_share()

    return json_body(
        {
            "id": metadata["id"]
        }
    )


def handle_upload(
    args,
    req
):
    share_id = args.get(
        "share_id",
        ""
    )

    if not valid_share_id(
        share_id
    ):
        return error_body(
            "Invalid share id."
        )

    metadata = get_share(
        share_id
    )

    if metadata is None:
        return error_body(
            "Share not found."
        )

    if len(
        metadata["files"]
    ) >= MAX_FILES_PER_SHARE:
        return error_body(
            "Too many files."
        )

    uploaded_file = (
        get_multipart_file()
    )

    if uploaded_file is None:
        return error_body(
            "No file received."
        )

    original_name = safe_filename(
        uploaded_file.filename
    )

    try:
        file_info = save_uploaded_file(
            share_id,
            uploaded_file.file,
            original_name,
            0
        )

    except ValueError as error:
        return error_body(
            str(error)
        )

    except OSError:
        return error_body(
            "Unable to store file."
        )

    metadata["files"].append(
        file_info
    )

    save_metadata(
        share_id,
        metadata
    )

    return json_body(
        {
            "id": file_info["id"],
            "name": file_info["name"],
            "size": file_info["size"],
            "date": file_info["date"]
        }
    )


def handle_info(
    share_id
):
    if not valid_share_id(
        share_id
    ):
        return error_body(
            "Invalid share id."
        )

    metadata = get_share(
        share_id
    )

    if metadata is None:
        return error_body(
            "Share not found."
        )

    return json_body(
        {
            "id": metadata["id"],
            "created": metadata["created"],
            "files": metadata["files"]
        }
    )


def create_file_response(
    path,
    download_name=None,
    content_type=None
):
    path = Path(
        path
    )

    if not path.is_file():
        return None

    if content_type is None:
        content_type = (
            mimetypes.guess_type(
                path.name
            )[0]
            or "application/octet-stream"
        )

    with path.open(
        "rb"
    ) as file_handle:
        body = file_handle.read()

    headers = {
        "Content-Length": str(
            len(body)
        )
    }

    if download_name:
        safe_name = (
            Path(
                download_name
            ).name
            .replace(
                '"',
                ""
            )
            .replace(
                "\r",
                ""
            )
            .replace(
                "\n",
                ""
            )
        )

        headers[
            "Content-Disposition"
        ] = (
            f'attachment; filename="{safe_name}"'
        )

    return {
        "status": 200,
        "content_type": content_type,
        "body": body,
        "headers": headers
    }


def handle_download(
    share_id,
    file_id
):
    if not valid_share_id(
        share_id
    ):
        return error_body(
            "Invalid share id."
        )

    if not valid_file_id(
        file_id
    ):
        return error_body(
            "Invalid file id."
        )

    metadata = get_share(
        share_id
    )

    if metadata is None:
        return error_body(
            "Share not found."
        )

    file_info = get_file_metadata(
        metadata,
        file_id
    )

    if file_info is None:
        return error_body(
            "File not found."
        )

    stored_file = (
        share_file_directory(
            share_id
        )
        / file_id
    )

    response = create_file_response(
        stored_file,
        download_name=file_info["name"]
    )

    if response is None:
        return error_body(
            "File not found."
        )

    return response


def handle_download_all(
    share_id
):
    if not valid_share_id(
        share_id
    ):
        return error_body(
            "Invalid share id."
        )

    metadata = get_share(
        share_id
    )

    if metadata is None:
        return error_body(
            "Share not found."
        )

    if not metadata.get(
        "files"
    ):
        return error_body(
            "No files found."
        )

    output = io.BytesIO()

    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_DEFLATED
    ) as archive:

        for file_info in metadata[
            "files"
        ]:
            stored_file = (
                share_file_directory(
                    share_id
                )
                / file_info["id"]
            )

            if stored_file.is_file():
                archive.write(
                    stored_file,
                    arcname=file_info[
                        "name"
                    ]
                )

    body = output.getvalue()

    return {
        "status": 200,
        "content_type": "application/zip",
        "body": body,
        "headers": {
            "Content-Length": str(
                len(body)
            ),
            "Content-Disposition": (
                f'attachment; '
                f'filename="fileshare-{share_id}.zip"'
            )
        }
    }


def index( req ):
    ensure_storage()

    args = parse_args(
        req
    )
    
    print( "INF: index: req: %s" % req )
    print( "INF: index: args: %s" % args )
    forms = {}
    if hasattr( req, "forms"):
        forms = req.forms
    
    print( "INF: index: forms: %s" % forms )

    action = args.get(
        "action",
        ""
    )

    share_id = args.get(
        "id",
        ""
    )

    if action == "create":
        return handle_create()

    if action == "upload":
        return handle_upload(
            args,
            req
        )

    if action == "download":
        return handle_download(
            share_id,
            args.get(
                "file",
                ""
            )
        )

    if action == "download_all":
        return handle_download_all(
            share_id
        )

    if share_id:
        file_id = args.get(
            "file",
            ""
        )

        if file_id:
            return handle_download(
                share_id,
                file_id
            )

        if args.get(
            "download"
        ) == "all":
            return handle_download_all(
                share_id
            )

        return handle_info(
            share_id
        )

    return html_body(
        "<!DOCTYPE html>"
        "<html>"
        "<head>"
        "<meta charset=\"utf-8\">"
        "<title>FileShare backend</title>"
        "</head>"
        "<body>"
        "<p>FileShare backend is running.</p>"
        "</body>"
        "</html>"
    )


def test_index():
    class Req:
        pass

    req = Req()

    req.args = "id=toto&q=coucou"

    result = index(
        req
    )

    print(
        "TEST INFO:"
    )

    print(
        result
    )

    req.args = "action=create"

    result = index(
        req
    )

    print(
        "TEST CREATE:"
    )

    print(
        result
    )


if __name__ == "__main__":
    test_index()
