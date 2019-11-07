import get_data_prancingturtle
import mysql_add_data
import create_html_files
import upload_html_aws
import traceback
import time


def main():
    try:
        new_sessions = get_data_prancingturtle.main()
        if new_sessions:
            mysql_add_data.main()
            create_html_files.main()
            upload_html_aws.main()
    except Exception:
        print("An error has occurred check the error_log.txt")
        log = open("../log/error_log.txt", "w")
        traceback.print_exc(file=log)
        log.close()
        x = input("Exit program: Y")


if __name__ == "__main__":
    main()
