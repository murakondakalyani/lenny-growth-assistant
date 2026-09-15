from app.artifacts.sanitizer import sanitize_html


def main():
    malicious_html = """
    <html>
        <body>
            <h1>Product Decision</h1>

            <script>
                alert("HACKED");
            </script>

            <button onclick="alert('XSS')">
                Click me
            </button>

            <iframe src="https://evil.example"></iframe>

            <a href="javascript:alert('XSS')">
                Dangerous Link
            </a>

            <p>Safe content remains.</p>
        </body>
    </html>
    """

    result = sanitize_html(malicious_html)

    print("=" * 80)
    print("ARTIFACT SANITIZER TEST")
    print("=" * 80)

    print("\nSANITIZED HTML:")
    print(result)

    assert "<script" not in result.lower()
    assert "<iframe" not in result.lower()
    assert "onclick" not in result.lower()
    assert "javascript:" not in result.lower()
    assert "Safe content remains." in result

    print("\n" + "=" * 80)
    print("SANITIZER TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()