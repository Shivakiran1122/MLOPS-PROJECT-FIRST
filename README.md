# 🧠 MLOPS_PROJECT-FIRST
**End‑to‑End ML Pipeline with MLflow, Docker, and Jenkins → Google Cloud Run**

![Jenkins Build](https://img.shields.io/badge/Jenkins-CI%2FCD-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-informational)
![Cloud Run](https://img.shields.io/badge/Google%20Cloud-Run-orange)

This repository demonstrates a **production‑minded MLOps pipeline**:
- Data ingestion & preprocessing
- Hyperparameter‑tuned model training (LightGBM)
- **MLflow** experiment tracking (datasets, params, metrics, model artifacts)
- Web inference app (Flask) + HTML UI
- **Docker** containerization
- **Jenkins CI/CD** that **builds & pushes** image to **GCR** and **deploys to Google Cloud Run** ✅

---

## 📚 Table of Contents
- [Repository Structure](#-repository-structure)
- [Architecture](#-architecture)
- [Environment Setup (Local)](#-environment-setup-local)
- [MLflow Experiment Tracking](#-mlflow-experiment-tracking)
- [Run the Pipeline](#-run-the-pipeline)
- [Run the Web App](#-run-the-web-app)
- [Docker (Local)](#-docker-local)
- [CI/CD on Jenkins → Cloud Run](#-cicd-on-jenkins--cloud-run)
  - [GCP Prereqs](#gcp-prereqs)
  - [Jenkins Credentials & Env Vars](#jenkins-credentials--env-vars)
  - [Pipeline Stages](#pipeline-stages)
  - [Full Jenkinsfile Example](#full-jenkinsfile-example)
- [Configuration Files](#-configuration-files)
- [Utilities & Logging](#-utilities--logging)
- [Dataset](#-dataset)
- [Testing](#-testing)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)
- [License](#-license)

---

## 📂 Repository Structure

```
MLOPS_TEST/
├── CI-CD Deployment Materials/
│   ├── STEPS FOR CI-CD Deployment on Jenkins.txt
│   └── STEPS.md
│
├── DATASET/
│   └── Hotel Reservations.csv/
│       ├── Hotel Reservations.csv
│       └── KAGGLE LINK.txt
│
├── PROJECT CODE/
│   ├── .gitignore
│   ├── Dockerfile
│   ├── Jenkinsfile
│   ├── application.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   ├── model_params.py
│   │   └── paths_config.py
│   │
│   ├── custom_jenkins/
│   │   └── Dockerfile
│   │
│   ├── notebook/
│   │   └── notebook.ipynb
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── training_pipeline.py
│   │
│   ├── requirements.txt
│   ├── setup.py
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── custom_exception.py
│   │   ├── data_ingestion.py
│   │   ├── data_preprocessing.py
│   │   ├── logger.py
│   │   └── model_training.py
│   │
│   ├── static/
│   │   └── style.css
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── utils/
│       ├── __init__.py
│       └── common_functions.py
│
└── README.md
```

---

## 🧠 Architecture

```
        +--------------------+
        |  Data Ingestion    |  <- reads curated CSVs
        +---------+----------+
                  |
                  v
        +--------------------+
        | Data Preprocessing |  <- clean/encode/split
        +---------+----------+
                  |
                  v
        +--------------------+
        |  Model Training    |  <- LightGBM + RandomizedSearchCV
        +---------+----------+
                  |
                  v
        +--------------------+
        |  MLflow Tracking   |  <- datasets, params, metrics, model
        +---------+----------+
                  |
                  v
        +--------------------+
        |   Flask Inference  |  <- application.py + templates/
        +---------+----------+
                  |
                  v
        +--------------------+
        |  Docker Container  |  <- PROJECT CODE/Dockerfile
        +---------+----------+
                  |
                  v
        +--------------------------+
        | Jenkins CI/CD -> GCR     |
        | then deploy to Cloud Run |
        +--------------------------+
```

---

## 🧰 Environment Setup (Local)

```bash
git clone https://github.com/Shivakiran1122/MLOPS_TEST.git
cd "MLOPS_TEST/PROJECT CODE"

python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

> Update `config/config.yaml`, `config/paths_config.py`, and `config/model_params.py` as needed.

---

## 🔬 MLflow Experiment Tracking

MLflow is used inside `src/model_training.py` (method `run()`):
- `mlflow.start_run()` wraps each training execution.
- Logs **train/test dataset snapshots** as artifacts:
  ```python
  mlflow.log_artifact(self.train_path, artifact_path="datasets")
  mlflow.log_artifact(self.test_path, artifact_path="datasets")
  ```
- Logs **final model** artifact (and optionally via `mlflow.sklearn.log_model`).
- Logs **hyperparameters** from tuned estimator: `mlflow.log_params(best_lgbm_model.get_params())`
- Logs **metrics**: accuracy, precision, recall, f1 via `mlflow.log_metrics(metrics)`

**Run MLflow UI locally:**
```bash
mlflow ui
# open http://127.0.0.1:5000  (or the URL printed by MLflow)
```

> Tip: set a custom experiment name at the start of training:
> ```python
> mlflow.set_experiment("hotel_reservations_experiments")
> ```

---

## ▶️ Run the Pipeline

The end‑to‑end training pipeline is in `pipeline/training_pipeline.py`, which calls into:
- `src/data_ingestion.py`
- `src/data_preprocessing.py`
- `src/model_training.py` (LightGBM + RandomizedSearchCV + MLflow)

Run:
```bash
python -m pipeline.training_pipeline
```

---

## 🌐 Run the Web App

Flask inference app with HTML UI:

```bash
python application.py
# open http://localhost:5000
```

Templates live in `templates/index.html` and styles in `static/style.css`.

---

## 🐳 Docker (Local)

```bash
# from PROJECT CODE/
docker build -t mlops_test_app:latest .
docker run -p 5000:5000 mlops_test_app:latest
# open http://localhost:5000
```

---

## 🚀 CI/CD on Jenkins → Cloud Run

This project includes a Jenkins Pipeline that:
1) Clones the repo  
2) Creates Python venv & installs dependencies  
3) Builds a Docker image and pushes to **Google Container Registry (GCR)**  
4) Deploys the image to **Google Cloud Run (serverless)**

### GCP Prereqs
- A GCP project (e.g., `mlops-new-447207`)
- Enable APIs: **Cloud Run**, **Container Registry** or **Artifact Registry**, **Cloud Build** (optional)
- A **service account** with roles:
  - `roles/run.admin`
  - `roles/storage.admin` (for GCR)
  - `roles/iam.serviceAccountUser`
- Download the service account key JSON (used by Jenkins credential `gcp-key`)

### Jenkins Credentials & Env Vars
Create these in Jenkins:
- **`github-token`** → for cloning private repos (or use https public if open)
- **`gcp-key`** (type: *Secret file*) → upload service account JSON

Environment variables used by the pipeline:
- `GCP_PROJECT` → your GCP project id (e.g., `mlops-new-447207`)
- `GCLOUD_PATH` → path to gcloud on the Jenkins agent (e.g., `/var/jenkins_home/google-cloud-sdk/bin`)

> Ensure **gcloud SDK** and **Docker** are installed on your Jenkins agent and the agent user can run Docker.

### Pipeline Stages
- **Clone** → `checkout scmGit(...)`
- **Setup Venv & Install** → `pip install -e .`
- **Build & Push Image** → `docker build` → `docker push gcr.io/$GCP_PROJECT/ml-project:latest`
- **Deploy to Cloud Run** → `gcloud run deploy` with `--allow-unauthenticated`

### Full Jenkinsfile Example

> **Note:** Adjust repo URL, branch (`main` vs `Master`), image name, and region as needed.

```groovy
pipeline{
    agent any

    environment {
        VENV_DIR   = 'venv'
        GCP_PROJECT = "mlops-new-447207"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(
                        branches: [[name: '*/main']],    // or */Master depending on your repo
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'github-token',
                            url: 'https://github.com/ORG_OR_USER/REPO.git'
                        ]]
                    )
                }
            }
        }

        stage('Setting up our Virtual Environment and Installing dependancies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and Installing dependancies............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Building and Pushing Docker Image to GCR'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Building and Pushing Docker Image to GCR.............'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet

                        docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .
                        docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                        '''
                    }
                }
            }
        }

        stage('Deploy to Google Cloud Run'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Deploy to Google Cloud Run.............'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}

                        gcloud run deploy ml-project \
                            --image=gcr.io/${GCP_PROJECT}/ml-project:latest \
                            --platform=managed \
                            --region=us-central1 \
                            --allow-unauthenticated
                        '''
                    }
                }
            }
        }
    }
}
```

---

## 🧾 Configuration Files
- `config/config.yaml` → high‑level pipeline settings (paths, flags, etc.)
- `config/model_params.py` → search space & defaults for LightGBM + RandomizedSearchCV
- `config/paths_config.py` → centralizes all filesystem paths (train/test/model output)

---

## 🪛 Utilities & Logging
- `src/logger.py` → centralized logging setup (`get_logger(__name__)`)
- `src/custom_exception.py` → wraps errors with stack traces & context
- `utils/common_functions.py` → helpers like `read_yaml`, `load_data`, etc.

---

## 📊 Dataset
- `DATASET/Hotel Reservations.csv/Hotel Reservations.csv` (Kaggle link in `KAGGLE LINK.txt`)
- Target column: `booking_status` (binary classification)
- Preprocessing & splits handled before training

---

## 🧪 Testing
Add tests (recommended) and run:
```bash
pytest -q
```

---

## 🔭 Future Enhancements
- MLflow **model registry** + stage promotion (Staging → Production)
- Add **DVC** for explicit data versioning
- Canary or blue‑green deploys on Cloud Run
- Prometheus/Grafana monitoring for latency & live metrics
- Automated drift detection & periodic retraining via Jenkins schedule
- CI checks: linting (flake8/ruff), unit tests, integration tests

---

## 👤 Author
**Shiva Kiran Dadishetty**  
GitHub: https://github.com/Shivakiran1122  
Focus: MLOps • Data Engineering • Generative AI




