import scripts.get_data_prancingturtle
import scripts.mysql_add_data
import scripts.create_html_files
import scripts.upload_html_aws


def main():
    new_sessions = scripts.get_data_prancingturtle.main()
    if new_sessions:
        scripts.mysql_add_data.main()
        scripts.create_html_files.main()
        scripts.upload_html_aws.main()


if __name__ == "__main__":
    main()
