import mailbox
import email
from email.header import decode_header, make_header


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

    for encoding in ("utf-8", "latin-1"):
        try:
            return payload.decode(encoding, errors = "replace")
        except UnicodeDecodeError:
            pass

    return payload.decode("utf-8", errors = "replace")


def extract_body(message):
    parts = []

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()

            if content_type == "text/plain":
                parts.append(decode_part(part))
    else:
        if message.get_content_type() == "text/plain":
            parts.append(decode_part(message))

    return "\n".join(parts)


def find_words(text, words):
    text_lower = text.lower()

    return [
        word for word in words
        if word.lower() in text_lower
    ]


def process_message(message, words, index, bRequireAllWords = True ):
    subject = decode_header_value(message.get("Subject"))
    sender = decode_header_value(message.get("From"))
    recipient = decode_header_value(message.get("To"))
    date = decode_header_value(message.get("Date"))

    body = extract_body(message)

    matches = find_words(
        subject + "\n" + body,
        words
    )
    
    if bRequireAllWords:
        if len(matches) != len(words):
            return
    else:
        if not matches:
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


def search_mbox(filename, words):
    print( "INF: loading mbox..." )
    mbox = mailbox.mbox(filename, create = False)

    try:
        for index, message in enumerate(mbox, start = 1):
            print( "index: %d\r" % index, end = "" )
            process_message(message, words, index)
    finally:
        mbox.close()


def main():
    filename = r"d:/takeout_sbre/Tous les messages, y compris ceux du dossier Spam -003.mbox"
    
    search_words = [ "serial", "choregraphe"]

    search_mbox(filename, search_words )

if __name__ == "__main__":
    main()
