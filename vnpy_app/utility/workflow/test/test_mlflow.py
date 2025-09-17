import unittest

from vnpy_app.utility.workflow.mlflow_api import Recorder, Experiment


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.uri = "file:./mlruns"
        self.experiment = Experiment(experiment_name="test", uri=self.uri, tags={'author': 'yc'})
        self.experiment.start_experiment()
        self.recorder = Recorder(experiment_id=self.experiment.experiment_id, uri=self.uri, tags={'task': 'modeling'})

    def test_recorder_log(self):
        self.recorder.start_run()
        self.recorder.log_metrics(**{'mse': 1.01, 'epoch': 1})
        self.recorder.log_params(**{'input_dim': 1024, 'output_dim': 1})
        self.recorder.end_run("FINISHED")

    def test_experiment(self):
        print(self.experiment.experiment_id)
        print(self.experiment.list_experiments())
        print(self.experiment.list_recorders())


if __name__ == '__main__':
    unittest.main()
