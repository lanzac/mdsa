from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.tools import ToolClient
from bioblend.galaxy.histories import HistoryClient
from bioblend.galaxy.datasets import DatasetClient
from bioblend.galaxy.tools.inputs import inputs
from bioblend.galaxy.jobs import JobsClient
from pprint import pprint
import time
from itertools import cycle

# ----------------------------------------------------------------------------
# Dataset 
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

# ----------------------------------------------------------------------------
# Upload File / Create history in Galaxy

def monitor_files(gi: GalaxyInstance, history_id: str, watch_states=["queued", "running"], update_interval=0.5):
    animation_chars = cycle(["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"])
    
    def update_display(hdas, animation_char):
        for hda in hdas:
            status_char = animation_char if hda["state"] in watch_states else "✅" if hda["state"] == "ok" else ""
            print(f'File: {hda["name"]} - State: {hda["state"]} {status_char}')

    hdas = gi.histories.show_history(history_id=history_id, contents=True, deleted=False)
    print(f"Number of files : {len(hdas)}")

    while any(hda["state"] in watch_states for hda in hdas):
        print("\033c", end="")
        update_display(hdas, next(animation_chars))
        time.sleep(update_interval)
        hdas = gi.histories.show_history(history_id=history_id, contents=True)

    print("\033c", end="")
    update_display(hdas, "")

def verify_unique_occurrences(A, B):
    for item in A:
        if B.count(item) != 1:
            return False
    return True

def create_history_with_inputs(gi: GalaxyInstance, tool_client: ToolClient, input_datasets_names: str) -> str:
    # Create a history client
    history_client = HistoryClient(gi)

    # Try to get the history
    hist_list = gi.histories.get_histories(name="Test")

    # Create input datasets
    input_datasets = Datasets(input_datasets_names)

    if not hist_list:
        # Create a new history
        new_history = history_client.create_history(name="Test")
        history_id = new_history['id']

        # Upload files to Galaxy
        for dataset in input_datasets:
            uploaded_dataset = tool_client.upload_file(dataset.get_name(), history_id, file_type=dataset.get_extension())

        monitor_files(gi, history_id)

    else:
        hist = hist_list[-1]
        history_id = hist['id']

        # Check if the datasets name fetched match with our list
        hdas = gi.histories.show_history(history_id=history_id, contents=True, deleted=False)
        history_dataset_names = [dataset["name"] for dataset in hdas]

        if (verify_unique_occurrences(input_datasets_names, history_dataset_names)):
            print("Check inputs names: OK")
        else:
            print("Error: input_datasets_names not found in history_dataset_names or may found multiple occurences of a dataset name.")
            print(f"input_datasets_names: {input_datasets_names}")
            print(f"history_dataset_names: {history_dataset_names}")
            quit()
    return history_id

def prepare_inputs(gi: GalaxyInstance, tool_client: ToolClient, tool_id: str, history_id: str) -> inputs:
    # Build tool in order to get informations about inputs
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
    return tool_inputs
# ----------------------------------------------------------------------------
# Job managment

def monitor_job(jobs_client: JobsClient, job_id: str, watch_states=["new", "queued", "running"], update_interval=0.5):
    animation_chars = cycle(["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"])

    def update_display(state, animation_char):
        status_char = animation_char if state in watch_states else "✅" if state == "ok" else ""
        print(f'Job: {job_id} - State: {state} {status_char}')
    
    current_state = jobs_client.get_state(job_id)

    while current_state in watch_states:
        print("\033c", end="")
        update_display(current_state, next(animation_chars))
        time.sleep(update_interval)
        current_state = jobs_client.get_state(job_id)

    print("\033c", end="")
    update_display(current_state, "")

# ----------------------------------------------------------------------------
def main():

    galaxy_url = "https://cheminformatics.usegalaxy.eu/"
    api_key = "f13ca86efb57e04dc2512e32d7dad95d"
    # Connect to the Galaxy instance
    gi = GalaxyInstance(url=galaxy_url, key=api_key)

    # Create a tool client
    tool_client = ToolClient(gi)

    # Set input datasets names
    input_datasets_names = ["test.pdb", "test.xtc", "test.ndx"]
    # Create a history based on input files
    history_id = create_history_with_inputs(gi, tool_client, input_datasets_names)

    # Set tool id : here it GROMACS RMSD for test
    tool_id = "toolshed.g2.bx.psu.edu/repos/chemteam/gmx_rmsd/gmx_rmsd/2022+galaxy0"

    # Prepare tool inputs
    tool_inputs = prepare_inputs(gi, tool_client, tool_id, history_id)

    # Run tool
    run_informations = tool_client.run_tool(tool_id=tool_id, history_id=history_id, tool_inputs=tool_inputs)

    # Get job id
    job_id = run_informations['jobs'][-1]['id']

    # Create Jobs client
    jobs_client = JobsClient(galaxy_instance=gi)

    # Monitor running job
    monitor_job(jobs_client, job_id)

    # Get outputs informations
    outputs_informations = jobs_client.get_outputs(job_id)

    # get outputs dataset id
    outputs_id = outputs_informations[-1]['dataset']['id']

    # Show outpus
    outputs_content = gi.datasets.show_dataset(dataset_id=outputs_id)
    pprint(outputs_content)

    # Download dataset
    gi.datasets.download_dataset(dataset_id=outputs_id, file_path='./')

    



if __name__ == "__main__":
    main()