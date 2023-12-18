from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.tools import ToolClient
from bioblend.galaxy.histories import HistoryClient
from bioblend.galaxy.datasets import DatasetClient
from bioblend.galaxy.tools.inputs import inputs
from pprint import pprint
import time
from itertools import cycle

class Dataset:
    def __init__(self, name):
        self._name = name
        self._extension = None

    def get_name(self):
        return self._name

    def get_extension(self):
        # Extraire l'extension du fichier
        extension = self._name.split('.')[-1]
        # Assigner l'extension à l'attribut
        self._extension = extension
        return extension
    

def Datasets(names):
    datasets = []
    for name in names:
        dataset = Dataset(name)
        datasets.append(dataset)
    return datasets

animation_chars = cycle(["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"])

def update_display(hdas, animation_char):
    for hda in hdas:
        # Utiliser l'animation pour les statuts 'queued' et 'running'
        if hda["state"] in ["queued", "running"]:
            status_char = animation_char
        elif hda["state"] == "ok":
            status_char = "✅"
        else:
            status_char = ""
        
        print(f'File {hda["name"]} - State: {hda["state"]} {status_char}')

def update_job_display(jobs_info, animation_char):
    for job in jobs_info:
        # Utiliser l'animation pour les statuts 'queued' et 'running'
        if job["state"] in ["queued", "running"]:
            status_char = animation_char
        elif job["state"] == "ok":
            status_char = "✅"
        else:
            status_char = ""
        
        print(f'Job {job["id"]} - State: {job["state"]} {status_char}')

# ---------------------------------

input_datasets_names = ["test.pdb", "test.xtc", "test.ndx"]
input_datasets = Datasets(input_datasets_names)

galaxy_url = "https://cheminformatics.usegalaxy.eu/"
api_key = "f13ca86efb57e04dc2512e32d7dad95d"

# Connect to the Galaxy instance
gi = GalaxyInstance(url=galaxy_url, key=api_key)

# Create a history client
history_client = HistoryClient(gi)

# Create a tool client
tool_client = ToolClient(gi)

# Try to get the history
hist_list = gi.histories.get_histories(name="Test")

if not hist_list:
    # Create a new history
    new_history = history_client.create_history(name="Test")
    history_id = new_history['id']

    # Upload files to Galaxy
    for dataset in input_datasets:
        uploaded_dataset = tool_client.upload_file(dataset.get_name(), history_id, file_type=dataset.get_extension())

    hdas = gi.histories.show_history(history_id=history_id, contents=True)
    print(f"Number of files : {len(hdas)}")


    # Vérifier l'état initial des fichiers
    hdas = gi.histories.show_history(history_id=history_id, contents=True)

    # Boucle principale
    while any(hda["state"] in ["queued", "running"] for hda in hdas):
        print("\033c", end="")  # Effacer la console
        update_display(hdas, next(animation_chars))
        
        # Attendre et mettre à jour l'état des fichiers
        time.sleep(0.5)
        hdas = gi.histories.show_history(history_id=history_id, contents=True)

    # Affichage final
    print("\033c", end="")  # Effacer la console
    update_display(hdas, "")

else:
    hist = hist_list[0]
    history_id = hist['id']

    # Check if the datasets name fetched match with our list
    hdas = gi.histories.show_history(history_id=history_id, contents=True)
    history_dataset_names = [dataset["name"] for dataset in hdas]

    if (set(input_datasets_names) == set(history_dataset_names)):
        print("Check inputs names: OK")
    else:
        print("Error: input_datasets_names different from history_dataset_names")
        quit()

tool_id = "toolshed.g2.bx.psu.edu/repos/chemteam/gmx_rmsd/gmx_rmsd/2022+galaxy0"
tool_build = tool_client.build(tool_id=tool_id, history_id=history_id)

hdas = gi.histories.show_history(history_id=history_id, contents=True)

# Prepare inputs
tool_inputs = inputs()
for input in tool_build["inputs"]:
    if (input['model_class'] == 'DataToolParameter'):
        files_extensions = input["extensions"]
        for hda in hdas:
            if (hda['extension'] in files_extensions):
                tool_inputs.set_dataset_param(name=input['name'], value={'values': [{'id': hda['id'], 'src': 'hda'}]})
                break


tool_id = "toolshed.g2.bx.psu.edu/repos/chemteam/gmx_rmsd/gmx_rmsd/2022+galaxy0"  # Assurez-vous que c'est le bon ID d'outil
tool_client.run_tool(tool_id=tool_id, history_id=history_id, tool_inputs=tool_inputs)

"-> update_job_display"



