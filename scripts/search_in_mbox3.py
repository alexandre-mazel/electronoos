import argparse
import email
import os
import re
import sys
from email.header import decode_header, make_header
from email.parser import BytesParser
from email.policy import default


SEARCH_WORDS = [
    "serial",
    "choregraphe",
    "pepper",
    "headbang"
]

BLOCK_SIZE = 8 * 1024 * 1024


def decode_header_value(value):
    if not value:
        return ""

    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return str(value)


def decode_part(part):
    payload = part.get_payload(decode = True)

    if payload is None:
        return ""

    charset = part.get_content_charset()

    if charset:
        try:
            return payload.decode(charset, errors = "replace")
        except (LookupError, UnicodeDecodeError):
            pass

    return payload.decode("utf-8", errors = "replace")


def extract_body(message):
    parts = []

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                continue

            if part.get_content_type() == "text/plain":
                parts.append(decode_part(part))

            elif part.get_content_type() == "text/html":
                if not parts:
                    parts.append(decode_part(part))
    else:
        if message.get_content_type() in ("text/plain", "text/html"):
            parts.append(decode_part(message))

    return "\n".join(parts)


def find_matches(text, words):
    text_lower = text.lower()

    return [
        word
        for word in words
        if word in text_lower
    ]


def process_message(raw_message, words, index):
    try:
        message = BytesParser(policy = default).parsebytes(raw_message)
    except Exception:
        return

    subject = decode_header_value(message.get("Subject"))
    sender = decode_header_value(message.get("From"))
    recipient = decode_header_value(message.get("To"))
    date = decode_header_value(message.get("Date"))
    body = extract_body(message)

    searchable_text = "\n".join([
        subject,
        sender,
        recipient,
        body
    ])

    matches = find_matches(searchable_text, words)

    #~ if not matches: # at least one
        #~ return
        
    if len(matches) != len(words):
        return

    print()
    print("=" * 80)
    print(f"MAIL #{index}")
    print("=" * 80)
    print(f"From    : {sender}")
    print(f"To      : {recipient}")
    print(f"Date    : {date}")
    print(f"Subject : {subject}")
    print(f"Matches : {', '.join(matches)}")
    print("-" * 80)
    print(body)
    print("=" * 80)
    sys.stdout.flush()


def process_chunk(chunk, words, message_number):
    positions = [
        match.start()
        for match in re.finditer(rb"(?m)^From ", chunk)
    ]

    if not positions:
        return chunk, message_number

    first_position = positions[0]

    if first_position > 0:
        prefix = chunk[:first_position]
        chunk = chunk[first_position:]
        positions = [
            match.start()
            for match in re.finditer(rb"(?m)^From ", chunk)
        ]
    else:
        prefix = b""

    for index in range(len(positions) - 1):
        start = positions[index]
        end = positions[index + 1]

        raw_message = chunk[start:end]

        process_message(
            raw_message,
            words,
            message_number
        )

        message_number += 1

    remaining_start = positions[-1]

    return chunk[remaining_start:], message_number


def search_mbox(filename, words):
    print("Search in mbox: '%s'" % filename ) 
    
    words = [w.lower() for w in words]
    print( "for words: %s" % words )
    
    file_size = os.path.getsize(filename)
    print( "file size: %dMB" % (file_size/(1024*1024)) )
    processed = 0
    message_number = 1
    remaining = b""
    last_percent = -1

    with open(filename, "rb", buffering = BLOCK_SIZE) as file:
        while True:
            chunk = file.read(BLOCK_SIZE)

            if not chunk:
                break

            processed += len(chunk)
            data = remaining + chunk

            positions = [
                match.start()
                for match in re.finditer(rb"(?m)^From ", data)
            ]

            if len(positions) < 2:
                remaining = data

                percent = int(processed * 100 / file_size)

                if percent != last_percent:
                    print(
                        f"\rScanning: {percent:3d}%",
                        end = "",
                        flush = True
                    )
                    last_percent = percent

                continue

            for index in range(len(positions) - 1):
                start = positions[index]
                end = positions[index + 1]

                raw_message = data[start:end]

                process_message(
                    raw_message,
                    words,
                    message_number
                )

                message_number += 1

            remaining = data[positions[-1]:]

            percent = int(processed * 100 / file_size)

            if percent != last_percent:
                print(
                    f"\rScanning: {percent:3d}%",
                    end = "",
                    flush = True
                )
                last_percent = percent

    if remaining:
        process_message(
            remaining,
            words,
            message_number
        )

    print("\rScanning: 100%")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "filename",
        help = "Path to the MBOX file"
    )

    parser.add_argument(
        "words",
        nargs = "*",
        help = "Words to search"
    )

    args = parser.parse_args()

    words = args.words if args.words else SEARCH_WORDS

    search_mbox(
        args.filename,
        words
    )


if __name__ == "__main__":
    #main()
    filename = "d:/takeout_sbre/Tous les messages, y compris ceux du dossier Spam -003.mbox"
    search_mbox(filename,["serial", "choregraphe"])
