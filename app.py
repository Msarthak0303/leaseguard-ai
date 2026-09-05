import base64
import json
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.reviewer import review_text
from src.parser import extract_text_from_pdf


# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


# ==========================================
# HTTP HANDLER
# ==========================================

class LeaseGuardHandler(BaseHTTPRequestHandler):

    # --------------------------------------
    # SEND JSON RESPONSE
    # --------------------------------------

    def send_json(self, data, status=200):

        response = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.end_headers()

        self.wfile.write(response)


    # --------------------------------------
    # SEND FRONTEND FILE
    # --------------------------------------

    def send_file(self, file_path, content_type):

        if not file_path.exists():

            self.send_error(
                404,
                "File not found"
            )

            return

        content = file_path.read_bytes()

        self.send_response(200)

        self.send_header(
            "Content-Type",
            content_type
        )

        self.send_header(
            "Content-Length",
            str(len(content))
        )

        self.end_headers()

        self.wfile.write(content)


    # ======================================
    # GET REQUESTS
    # ======================================

    def do_GET(self):

        path = urlparse(
            self.path
        ).path


        if path == "/":

            self.send_file(
                FRONTEND_DIR / "index.html",
                "text/html; charset=utf-8"
            )


        elif path == "/style.css":

            self.send_file(
                FRONTEND_DIR / "style.css",
                "text/css; charset=utf-8"
            )


        elif path == "/app.js":

            self.send_file(
                FRONTEND_DIR / "app.js",
                "application/javascript; charset=utf-8"
            )


        else:

            self.send_error(
                404,
                "Not found"
            )


    # ======================================
    # POST REQUESTS
    # ======================================

    def do_POST(self):

        path = urlparse(
            self.path
        ).path


        if path == "/api/review":

            self.handle_text_review()


        elif path == "/api/upload":

            self.handle_pdf_upload()


        else:

            self.send_error(
                404,
                "Not found"
            )


    # ======================================
    # READ JSON BODY
    # ======================================

    def read_json_body(self):

        content_length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )


        if content_length <= 0:

            raise ValueError(
                "Empty request body."
            )


        body = self.rfile.read(
            content_length
        )


        return json.loads(
            body.decode("utf-8")
        )


    # ======================================
    # TEXT REVIEW
    # ======================================

    def handle_text_review(self):

        try:

            data = self.read_json_body()

            lease_text = data.get(
                "text",
                ""
            )


            if not lease_text.strip():

                self.send_json(
                    {
                        "error":
                        "No lease agreement text was provided."
                    },
                    status=400
                )

                return


            result = review_text(
                lease_text
            )


            self.send_json(
                result
            )


        except json.JSONDecodeError:

            self.send_json(
                {
                    "error":
                    "Invalid JSON request."
                },
                status=400
            )


        except Exception as error:

            self.send_json(
                {
                    "error":
                    str(error)
                },
                status=500
            )


    # ======================================
    # PDF UPLOAD
    # ======================================

    def handle_pdf_upload(self):

        temp_path = None


        try:

            data = self.read_json_body()


            filename = data.get(
                "filename",
                ""
            )


            pdf_base64 = data.get(
                "file",
                ""
            )


            # --------------------------------
            # VALIDATE FILE NAME
            # --------------------------------

            if not filename:

                self.send_json(
                    {
                        "error":
                        "No filename was provided."
                    },
                    status=400
                )

                return


            if not filename.lower().endswith(".pdf"):

                self.send_json(
                    {
                        "error":
                        "Only PDF files are supported."
                    },
                    status=400
                )

                return


            # --------------------------------
            # VALIDATE FILE DATA
            # --------------------------------

            if not pdf_base64:

                self.send_json(
                    {
                        "error":
                        "No PDF file was provided."
                    },
                    status=400
                )

                return


            # --------------------------------
            # DECODE BASE64
            # --------------------------------

            try:

                pdf_bytes = base64.b64decode(
                    pdf_base64,
                    validate=True
                )

            except Exception:

                self.send_json(
                    {
                        "error":
                        "Invalid PDF data."
                    },
                    status=400
                )

                return


            # --------------------------------
            # BASIC FILE SIZE PROTECTION
            # --------------------------------

            max_size = 10 * 1024 * 1024

            if len(pdf_bytes) > max_size:

                self.send_json(
                    {
                        "error":
                        "PDF is too large. Maximum size is 10 MB."
                    },
                    status=400
                )

                return


            # --------------------------------
            # CREATE TEMPORARY PDF
            # --------------------------------

            with tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False
            ) as temp_file:

                temp_file.write(
                    pdf_bytes
                )

                temp_path = temp_file.name


            # --------------------------------
            # EXTRACT PDF TEXT
            # --------------------------------

            lease_text = extract_text_from_pdf(
                temp_path
            )


            if not lease_text.strip():

                self.send_json(
                    {
                        "error":
                        "No readable text was found in the PDF. "
                        "The PDF may contain scanned images."
                    },
                    status=400
                )

                return


            # --------------------------------
            # REVIEW LEASE
            # --------------------------------

            result = review_text(
                lease_text
            )


            # --------------------------------
            # RETURN SOURCE INFORMATION
            # --------------------------------

            result["source_file"] = filename

            result["extracted_text"] = lease_text


            # --------------------------------
            # SEND RESULT
            # --------------------------------

            self.send_json(
                result
            )


        except json.JSONDecodeError:

            self.send_json(
                {
                    "error":
                    "Invalid JSON request."
                },
                status=400
            )


        except Exception as error:

            self.send_json(
                {
                    "error":
                    str(error)
                },
                status=500
            )


        finally:

            # --------------------------------
            # DELETE TEMPORARY PDF
            # --------------------------------

            if temp_path:

                try:

                    Path(
                        temp_path
                    ).unlink(
                        missing_ok=True
                    )

                except Exception:

                    pass


# ==========================================
# START SERVER
# ==========================================

def main():

    host = "0.0.0.0"

    port = 8000


    server = ThreadingHTTPServer(
        (host, port),
        LeaseGuardHandler
    )


    print()

    print(
        "========================================"
    )

    print(
        "        LEASEGUARD AI - PHASE 3"
    )

    print(
        "========================================"
    )

    print()

    print(
        "Server running at:"
    )

    print(
        f"http://localhost:{port}"
    )

    print()

    print(
        "PDF upload endpoint:"
    )

    print(
        "POST /api/upload"
    )

    print()

    print(
        "Text review endpoint:"
    )

    print(
        "POST /api/review"
    )

    print()

    print(
        "Press CTRL+C to stop."
    )

    print()


    server.serve_forever()


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    main()