import os


def get_first_zip_in_job(job):
    try:
        job_folder_path = os.path.join(os.getcwd(), job)

        if not os.path.exists(job_folder_path):
            raise FileNotFoundError("The 'job' folder does not exist.")

        contents = [
            item
            for item in os.listdir(job_folder_path)
            if os.path.isdir(os.path.join(job_folder_path, item))
        ]
        if not contents:
            raise FileNotFoundError("The 'job' folder is empty or contains no folders.")

        contents.sort(key=lambda x: os.path.getmtime(os.path.join(job_folder_path, x)))
        oldest_folder = contents[0]

        oldest_folder_path = os.path.join(job_folder_path, oldest_folder)
        folder_contents = os.listdir(oldest_folder_path)
        zip_file = None
        for item in folder_contents:
            if item.endswith(".zip"):
                zip_file = item
                break

        if not zip_file:
            raise FileNotFoundError(
                f"No .zip files found in the folder '{oldest_folder}'."
            )

        file_name = os.path.splitext(zip_file)[0]

        return oldest_folder, zip_file, file_name

    except FileNotFoundError as e:
        print(e)
        return None, None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None
