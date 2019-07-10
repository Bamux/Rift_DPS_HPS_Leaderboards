import get_data_prancingturtle
import mysql_add_data
import create_html_files
import upload_html_aws
import mysql_connect_config


def main():
    new_sessions = get_data_prancingturtle.main()
    if new_sessions:
        mysql_add_data.main()
        create_html_files.main()
        try:
            upload_html_aws.main()
        except:
            pass


if __name__ == "__main__":
    main()
