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

# ---------------------------------

galaxy_url = "https://cheminformatics.usegalaxy.eu/"
api_key = "f13ca86efb57e04dc2512e32d7dad95d"

# Connect to the Galaxy instance
gi = GalaxyInstance(url=galaxy_url, key=api_key)

# Create a history client
history_client = HistoryClient(gi)

# Create a tool client
tool_client = ToolClient(gi)

# Create a new history
new_history = history_client.create_history(name="Test")
history_id = new_history['id']


# Load inputs files
input_datasets = Datasets(["test.pdb", "test.xtc", "test.ndx"])

for dataset in input_datasets:
    uploaded_dataset = tool_client.upload_file(dataset.get_name(), history_id, file_type=dataset.get_extension())

# pdb_dataset = tool_client.upload_file("test.pdb", history_id, file_type='pdb')
# xtc_dataset = tool_client.upload_file("test.xtc", history_id, file_type='xtc')
# ndx_dataset = tool_client.upload_file("test.ndx", history_id, file_type='ndx')

hdas = gi.histories.show_history(history_id=history_id, contents=True)
print(f"Number of files : {len(hdas)}")


state = 'queued'

while state == 'queued':
    hdas = gi.histories.show_history(history_id=history_id, contents=True)

    for history in hdas:
        if history["state"] == 'queued':
            continue
        elif history["state"] == 'ok':
            print(f'Done for file {history["name"]}')

    time.sleep(5)
    



# hist = gi.histories.get_histories(name="Test")[0]
# hist_id = hist["id"]
# hdas = gi.histories.show_history(history_id=hist_id, contents=True)

# # Prepare inputs
# tool_inputs = inputs()

# tool_inputs.set_dataset_param(name='structure_input', value={'values': [{'id': '4838ba20a6d86765630cfabed1e61220', 'src': 'hda'}]})
# tool_inputs.set_dataset_param(name='traj_input', value={'values': [{'id': '4838ba20a6d86765a5dd52266e4b89b1', 'src': 'hda'}]})
# tool_inputs.set_dataset_param(name='ndx_input', value={'values': [{'id': '4838ba20a6d867650126ad6178df52ac', 'src': 'hda'}]})

# tool_id = "toolshed.g2.bx.psu.edu/repos/chemteam/gmx_rmsd/gmx_rmsd/2022+galaxy0"  # Assurez-vous que c'est le bon ID d'outil
# # response = tool_client.build(tool_id=tool_id, history_id=hist_id)
# response = tool_client.run_tool(tool_id=tool_id, history_id=hist_id, tool_inputs=tool_inputs)

# pprint(response)
