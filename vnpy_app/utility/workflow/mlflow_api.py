import pickle
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import mlflow


class Recorder:
    # status type
    STATUS_S = "SCHEDULED"
    STATUS_R = "RUNNING"
    STATUS_FI = "FINISHED"
    STATUS_FA = "FAILED"

    def __init__(self, experiment_id, uri, tags=None):
        self.run_id = None
        self.tags = tags
        self.experiment_id = experiment_id
        self._uri = uri
        self._artifact_uri = None
        self.client = mlflow.tracking.MlflowClient(tracking_uri=uri)
        # set the tracking uri
        mlflow.set_tracking_uri(uri)

        self.start_time = None
        self.end_time = None

    @property
    def uri(self):
        return self._uri

    @property
    def artifact_uri(self):
        return self._artifact_uri

    def get_run(self):
        return self.client.get_run(self.run_id)

    def start_run(self):
        # start the run
        run = self.client.create_run(self.experiment_id, self.start_time, self.tags)
        # save the run id and artifact_uri
        self.run_id = run.info.run_id
        self._artifact_uri = run.info.artifact_uri
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return run

    def end_run(self, status: str = STATUS_S):
        assert status in [
            Recorder.STATUS_S,
            Recorder.STATUS_R,
            Recorder.STATUS_FI,
            Recorder.STATUS_FA,
        ], f"The status type {status} is not supported."
        self.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.client.set_terminated(self.run_id, status)

    def log_params(self, **kwargs):
        for name, data in kwargs.items():
            self.client.log_param(self.run_id, name, data)

    def log_metrics(self, step=None, **kwargs):
        for name, data in kwargs.items():
            self.client.log_metric(self.run_id, name, data, step=step)

    def log_artifacts(self, local_path=None, artifact_path: Optional[str] = None, **kwargs):
        if local_path is not None:
            path = Path(local_path)
            if path.is_dir():
                self.client.log_artifacts(self.run_id, local_path, artifact_path)
            else:
                self.client.log_artifact(self.run_id, local_path, artifact_path)
        else:
            temp_dir = Path(tempfile.mkdtemp()).resolve()
            for name, data in kwargs.items():
                path = temp_dir / name
                with open(path, "wb") as f:
                    # noinspection PyTypeChecker
                    pickle.dump(data, f)
                self.client.log_artifact(self.run_id, temp_dir / name, artifact_path)
            shutil.rmtree(temp_dir)

    def set_tags(self, **kwargs):
        for name, data in kwargs.items():
            self.client.set_tag(self.run_id, name, data)

    def delete_tags(self, *keys):
        for key in keys:
            self.client.delete_tag(self.run_id, key)

    def get_artifact_uri(self):
        return self.artifact_uri

    def list_artifacts(self, artifact_path=None):
        artifacts = self.client.list_artifacts(self.run_id, artifact_path)
        return [art.path for art in artifacts]

    def download_artifact(self, path: str, dst_path: Optional[str] = None):
        path = self.client.download_artifacts(self.run_id, path, dst_path)
        with open(path, "rb") as f:
            data = pickle.load(f)
        return data

    def list_metrics(self):
        run = self.client.get_run(self.run_id)
        return run.data.metrics

    def list_params(self):
        run = self.client.get_run(self.run_id)
        return run.data.params

    def list_tags(self):
        run = self.client.get_run(self.run_id)
        return run.data.tags


class Experiment:
    def __init__(self, experiment_name, uri, tags=None):
        self.experiment_id = None
        self.experiment_name = experiment_name
        self.tags = tags
        self._uri = uri
        self.client = mlflow.tracking.MlflowClient(tracking_uri=uri)
        # set the tracking uri
        mlflow.set_tracking_uri(uri)

    @property
    def uri(self):
        return self._uri

    def create_experiment(self):
        # set the tracking uri
        mlflow.set_tracking_uri(self.uri)
        # create the experiment
        experiment_id = self.client.create_experiment(self.experiment_name, tags=self.tags)
        experiment = self.client.get_experiment(experiment_id)
        return experiment

    def _get_or_create_experiment(self, ):
        experiment_name = self.experiment_name
        experiments = self.list_experiments()
        experiment_names = [exp.name for exp in experiments]
        if experiment_name is not None and experiment_name in experiment_names:
            return self.get_experiment_by_name(experiment_name)
        else:
            return self.create_experiment()

    def start_experiment(self):
        # start the experiment
        experiment = self._get_or_create_experiment()
        # save the experiment id
        self.experiment_id = experiment.experiment_id
        return experiment

    def end_experiment(self):
        # end the experiment
        pass

    def get_experiment(self):
        return self.client.get_experiment(self.experiment_id)

    def get_experiment_by_name(self, experiment_name):
        return self.client.get_experiment_by_name(experiment_name)

    def delete_experiment(self):
        return self.client.delete_experiment(self.experiment_id)

    def list_experiments(self):
        return self.client.search_experiments()

    def list_recorders(self, max_results=10):
        runs = self.client.search_runs(self.experiment_id, run_view_type=3, max_results=max_results)
        rids = [n.info.run_id for n in runs]
        recorders = list()
        for rid in rids:
            recorder = Recorder(experiment_id=self.experiment_id, uri=self.uri)
            recorder.run_id = rid
            recorders.append(recorder)

        return dict(zip(rids, recorders))
