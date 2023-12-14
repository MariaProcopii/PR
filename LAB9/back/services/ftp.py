import os

from ftplib import FTP


class FtpService:

    link = None

    @staticmethod
    def upload(name, content):
        try:
            FtpService._ftp_server = FTP("138.68.98.108")
            FtpService._ftp_server.login("yourusername", "yourusername")
            FtpService._ftp_server.cwd("faf-212")
            FtpService._ftp_server.cwd("maria-procopii")

            with open(f"files/{name}", "w") as tmp_file:
                tmp_file.write(content)

            with open(f"files/{name}", "rb") as fp:
                FtpService._ftp_server.storbinary(f"STOR {name}", fp)

            FtpService.link = f"ftp://yourusername:yourusername@138.68.98.108/faf-212/maria-procopii/{name}"

            os.remove(f"files/{name}")
            FtpService._ftp_server.quit()
            return True
        except Exception as e:
            print(e)
            return False
