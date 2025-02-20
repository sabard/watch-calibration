class InternetArchive:

    def __init__(self):
        pass

    def upload(self):
        pass

    def generate_metadata_file(self):
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cwd = os.getcwd()
        print(parent_dir, cwd)

        print(os.listdir(cwd))

        with open('metadata.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["identifier", "file"])
            writer.writeheader()
            writer.writerow({
                "identifier": "watch-calibration",
                "file": "watch-calibration.cf"
            })
