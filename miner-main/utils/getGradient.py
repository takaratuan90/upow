import os


def find_gradient(destination):
    try:
        destination_path = os.path.join(os.getcwd(), destination)

        if not os.path.exists(destination_path):
            raise FileNotFoundError(f"The '{destination}' folder does not exist.")

        contents = [
            item
            for item in os.listdir(destination_path)
            if os.path.isdir(os.path.join(destination_path, item))
        ]
        if not contents:
            raise FileNotFoundError(
                f"The '{destination}' folder is empty or contains no folders."
            )

        contents.sort(key=lambda x: os.path.getmtime(os.path.join(destination_path, x)))
        oldest_folder = contents[0]

        oldest_folder_path = os.path.join(destination_path, oldest_folder)
        folder_contents = os.listdir(oldest_folder_path)
        pth_file = None
        for item in folder_contents:
            if item.endswith(".pth"):
                pth_file = item
                break

        if not pth_file:
            raise FileNotFoundError(
                f"No .pth files found in the folder '{oldest_folder}'."
            )

        just_name = os.path.splitext(pth_file)[0]

        return oldest_folder, pth_file, just_name

    except FileNotFoundError as e:
        print(e)
        return None, None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None
