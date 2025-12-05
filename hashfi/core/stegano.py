from PIL import Image
import io


def encode_lsb(image_file, secret_text):
    """Encodes text into an image using LSB steganography."""
    img = Image.open(image_file)
    img = img.convert("RGB")
    pixels = img.load()

    # Convert text to binary
    binary_text = "".join(format(ord(char), "08b") for char in secret_text)
    binary_text += "1111111111111110"  # Delimiter

    data_index = 0
    width, height = img.size

    for y in range(height):
        for x in range(width):
            if data_index < len(binary_text):
                r, g, b = pixels[x, y]

                # Modify the Least Significant Bit of the Red channel
                if binary_text[data_index] == "0":
                    r &= ~1
                else:
                    r |= 1

                pixels[x, y] = (r, g, b)
                data_index += 1
            else:
                break
        if data_index >= len(binary_text):
            break

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output


def decode_lsb(image_file):
    """Decodes text from an image using LSB steganography."""
    img = Image.open(image_file)
    img = img.convert("RGB")
    pixels = img.load()

    binary_text = ""
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            # Extract LSB from Red channel
            binary_text += str(r & 1)

            # Check for delimiter every 8 bits (1 byte) + 16 bits (2 bytes delimiter)
            # Optimization: Check for delimiter only when we have enough bits
            if len(binary_text) >= 16 and binary_text[-16:] == "1111111111111110":
                # Found delimiter
                binary_data = binary_text[:-16]
                text = ""
                for i in range(0, len(binary_data), 8):
                    byte = binary_data[i : i + 8]
                    text += chr(int(byte, 2))
                return text

    return "No hidden message found or image too large/corrupted."
