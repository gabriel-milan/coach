import json

from coach import models


def test_model():
    # Schema:
    # id = models.AutoField(primary_key=True)
    # date_created = models.DateTimeField(auto_now_add=True)
    # date_modified = models.DateTimeField(auto_now=True)
    # description = models.TextField(blank=True, null=True)
    # config = models.TextField(blank=True, null=True)
    # Create instances and assert results of model schema
    model = models.Model(
        description="Test model",
        config=json.dumps({"test": "test"})
    )
    assert model.id is None
    assert model.date_created is None
    assert model.date_modified is None
    assert model.description == "Test model"
    assert model.config == json.dumps({"test": "test"})
    assert json.loads(model.config) == {'test': 'test'}
    model.save()
    assert model.id is not None
    assert model.date_created is not None
    assert model.date_modified is not None
    assert model.description == "Test model"
    assert model.config == json.dumps({"test": "test"})
    assert json.loads(model.config) == {'test': 'test'}
    model.delete()
    assert model.id is None


def test_script():
    # Schema:
    # id = models.AutoField(primary_key=True)
    # date_created = models.DateTimeField(auto_now_add=True)
    # date_modified = models.DateTimeField(auto_now=True)
    # description = models.TextField(blank=True, null=True)
    # path = models.TextField()
    # Create instances and assert results of model schema
    script = models.Script(
        description="Test script",
        path="tests/models/test_create.py"
    )
    assert script.id is None
    assert script.date_created is None
    assert script.date_modified is None
    assert script.description == "Test script"
    assert script.path == "tests/models/test_create.py"
    script.save()
    assert script.id is not None
    assert script.date_created is not None
    assert script.date_modified is not None
    assert script.description == "Test script"
    assert script.path == "tests/models/test_create.py"
    script.delete()
    assert script.id is None


def test_parameters():
    # Schema:
    # id = models.AutoField(primary_key=True)
    # date_created = models.DateTimeField(auto_now_add=True)
    # date_modified = models.DateTimeField(auto_now=True)
    # description = models.TextField(blank=True, null=True)
    # config = models.TextField(blank=True, null=True)
    # Create instances and assert results of model schema
    parameters = models.Parameters(
        description="Test parameters",
        config=json.dumps({"test": "test"})
    )
    assert parameters.id is None
    assert parameters.date_created is None
    assert parameters.date_modified is None
    assert parameters.description == "Test parameters"
    assert parameters.config == json.dumps({"test": "test"})
    assert json.loads(parameters.config) == {'test': 'test'}
    parameters.save()
    assert parameters.id is not None
    assert parameters.date_created is not None
    assert parameters.date_modified is not None
    assert parameters.description == "Test parameters"
    assert parameters.config == json.dumps({"test": "test"})
    assert json.loads(parameters.config) == {'test': 'test'}
    parameters.delete()
    assert parameters.id is None


def test_weights():
    # Schema:
    # id = models.AutoField(primary_key=True)
    # date_created = models.DateTimeField(auto_now_add=True)
    # date_modified = models.DateTimeField(auto_now=True)
    # description = models.TextField(blank=True, null=True)
    # path = models.TextField()
    # Create instances and assert results of model schema
    weights = models.Weights(
        description="Test weights",
        path="tests/models/test_create.py"
    )
    assert weights.id is None
    assert weights.date_created is None
    assert weights.date_modified is None
    assert weights.description == "Test weights"
    assert weights.path == "tests/models/test_create.py"
    weights.save()
    assert weights.id is not None
    assert weights.date_created is not None
    assert weights.date_modified is not None
    assert weights.description == "Test weights"
    assert weights.path == "tests/models/test_create.py"
    weights.delete()
    assert weights.id is None


def test_status():
    # Schema:
    # id = models.AutoField(primary_key=True)
    # status = models.TextField()
    # description = models.TextField(blank=True, null=True)
    # Create instances and assert results of model schema
    status = models.Status(
        status="Test status",
        description="Test description"
    )
    assert status.id is None
    assert status.status == "Test status"
    assert status.description == "Test description"
    status.save()
    assert status.id is not None
    assert status.status == "Test status"
    assert status.description == "Test description"
    status.delete()
    assert status.id is None


def test_tag():
    # Schema:
    # id = models.AutoField(primary_key=True)
    # name = models.TextField()
    # description = models.TextField(blank=True, null=True)
    # Create instances and assert results of model schema
    tag = models.Tag(
        name="Test tag",
        description="Test description"
    )
    assert tag.id is None
    assert tag.name == "Test tag"
    assert tag.description == "Test description"
    tag.save()
    assert tag.id is not None
    assert tag.name == "Test tag"
    assert tag.description == "Test description"
    tag.delete()
    assert tag.id is None


def test_run():
    # Schema:
    # id = models.AutoField(primary_key=True)
    # date_created = models.DateTimeField(auto_now_add=True)
    # date_modified = models.DateTimeField(auto_now=True)
    # description = models.TextField(blank=True, null=True)
    # model = models.ForeignKey(Model, on_delete=models.CASCADE)
    # script = models.ForeignKey(Script, on_delete=models.CASCADE)
    # parameters = models.ForeignKey(Parameters, on_delete=models.CASCADE)
    # weights = models.ForeignKey(Weights, on_delete=models.CASCADE)
    # status = models.ForeignKey(Status, on_delete=models.CASCADE)
    # tags = models.ManyToManyField(Tag)
    # train_score = models.FloatField(blank=True, null=True)
    # validation_score = models.FloatField(blank=True, null=True)
    # Create instances and assert results of model schema
    model = models.Model(
        description="Test model",
        config=json.dumps({"test": "test"})
    )
    model.save()
    script = models.Script(
        description="Test script",
        path="tests/models/test_create.py"
    )
    script.save()
    parameters = models.Parameters(
        description="Test parameters",
        config=json.dumps({"test": "test"})
    )
    parameters.save()
    weights = models.Weights(
        description="Test weights",
        path="tests/models/test_create.py"
    )
    weights.save()
    status = models.Status(
        status="Test status",
        description="Test description"
    )
    status.save()
    tag = models.Tag(
        name="Test tag",
        description="Test description"
    )
    tag.save()
    run = models.Run(
        description="Test run",
        model=model,
        script=script,
        parameters=parameters,
        weights=weights,
        status=status,
        train_score=0.5,
        validation_score=0.5,
    )
    assert run.id is None
    assert run.date_created is None
    assert run.date_modified is None
    assert run.description == "Test run"
    assert run.model == model
    assert run.script == script
    assert run.parameters == parameters
    assert run.weights == weights
    assert run.status == status
    assert run.train_score == 0.5
    assert run.validation_score == 0.5
    run.save()
    run.tags.add(tag)
    assert run.id is not None
    assert run.date_created is not None
    assert run.date_modified is not None
    assert run.description == "Test run"
    assert run.model == model
    assert run.script == script
    assert run.parameters == parameters
    assert run.weights == weights
    assert run.status == status
    assert tag in run.tags.all()
    assert run.train_score == 0.5
    assert run.validation_score == 0.5
    run.train_score = 0.6
    run.validation_score = 0.6
    run.save()
    assert run.id is not None
    assert run.date_created is not None
    assert run.date_modified is not None
    assert run.description == "Test run"
    assert run.model == model
    assert run.script == script
    assert run.parameters == parameters
    assert run.weights == weights
    assert run.status == status
    assert tag in run.tags.all()
    assert run.train_score == 0.6
    assert run.validation_score == 0.6
    run.delete()
    assert run.id is None
