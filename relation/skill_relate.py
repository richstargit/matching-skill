tech_relate = {
    # --- Core Languages ---
    "JavaScript": ["TypeScript"],
    "TypeScript": ["JavaScript"],
    "Java": ["Kotlin"],
    "Kotlin": ["Java"],
    "Python": [],
    "R": [],
    "Swift": [],
    "Dart": [],

    # --- Frontend Frameworks ---
    "React": ["Vue.js", "Angular", "Next.js"],
    "Vue.js": ["React", "Angular", "Nuxt.js"],
    "Next.js": ["React", "Nuxt.js"],
    "Nuxt.js": ["Vue.js", "Next.js"],
    "Tailwind": ["CSS3"],
    "Vite": ["Webpack"],
    "Webpack": ["Vite"],
    "Storybook": ["React", "Vue.js", "UI/UX"],

    # --- Backend Frameworks / APIs ---
    "Node.js": ["Deno"],
    "Express.js": ["FastAPI", "Flask", "Django"],
    "Spring Boot": ["Micronaut", "Quarkus"],
    "FastAPI": ["Flask", "Django"],
    "Flask": ["FastAPI", "Django"],
    "Django": ["Flask", "FastAPI"],
    "REST API": ["GraphQL"],

    # --- Databases ---
    "MySQL": ["PostgreSQL", "Oracle"],
    "PostgreSQL": ["MySQL", "Oracle"],
    "Oracle": ["MySQL", "PostgreSQL"],
    "MongoDB": ["NoSQL"],
    "NoSQL": ["MongoDB"],
    "SQL Scripting": ["PL/SQL"],
    "Database Design": ["Database Development"],
    "Database Management": ["Database Development"],

    # --- Cloud ---
    "AWS": ["Azure", "GCP"],
    "Azure": ["AWS", "GCP"],
    "GCP": ["AWS", "Azure"],
    "AWS CLI": ["Azure CLI", "GCP CLI"],
    "Azure CLI": ["AWS CLI", "GCP CLI"],
    "CloudFormation": ["Terraform"],
    "Vertex AI": ["SageMaker"],

    # --- Infra / DevOps ---
    "Terraform": ["CloudFormation", "Ansible", "Puppet", "Chef"],
    "Ansible": ["Puppet", "Chef", "Terraform"],
    "Puppet": ["Ansible", "Chef"],
    "Chef": ["Ansible", "Puppet"],
    "Docker": ["Kubernetes"],
    "Kubernetes": ["Docker"],

    # --- MLOps / Distributed ---
    "Weights & Biases": ["MLflow"],
    "MLflow": ["Weights & Biases"],
    "TorchServe": ["BentoML", "Seldon"],
    "BentoML": ["TorchServe", "Seldon"],
    "Seldon": ["TorchServe", "BentoML"],
    "Ray": ["Dask", "Spark Streaming"],

    # --- Networking ---
    "VPN": ["Proxy Servers"],
    "Proxy Servers": ["VPN"],
    "Wireless Network": ["Wired Network"],
    "Wired Network": ["Wireless Network"],

    # --- Storage ---
    "NAS Storage": ["SAN"],
    "SAN": ["NAS Storage"],
    "EMC Storage": ["NAS Storage", "SAN"],
    "Storage & Backup": ["NAS Storage", "SAN"],
    "Backup Software": ["Backup/Restore"],

    # --- Reporting / Visualization ---
    "Tableau": ["PowerBI", "Qlik Sense", "Excel"],
    "PowerBI": ["Tableau", "Qlik Sense", "Excel"],
    "Qlik Sense": ["Tableau", "PowerBI"],
    "Excel": ["Tableau", "PowerBI"],
    "Crystal Report": ["Fast Report"],
    "Fast Report": ["Crystal Report"],

    # --- Data / ETL ---
    "Talend": ["Informatica", "Apache NiFi"],
    "Informatica": ["Talend", "Apache NiFi"],
    "Apache NiFi": ["Talend", "Informatica"],

    # --- Data Visualization / Reporting ---
    "PowerBI": ["Tableau", "Qlik Sense", "Excel"],
    "Tableau": ["PowerBI", "Qlik Sense", "Excel"],
    "Qlik Sense": ["Tableau", "PowerBI"],
    "Crystal Report": ["Fast Report"],
    "Fast Report": ["Crystal Report"],
    "Looker": ["Metabase", "Superset"],
    "Metabase": ["Looker", "Superset"],
    "Superset": ["Looker", "Metabase"],

    # --- Machine Learning / Deep Learning ---
    "scikit-learn": ["PyTorch", "TensorFlow"],
    "PyTorch": ["TensorFlow", "Keras"],
    "TensorFlow": ["PyTorch", "Keras"],
    "Keras": ["TensorFlow", "PyTorch"],
    "Transformers": ["TensorFlow", "PyTorch", "Keras"],
    "Detectron2": ["YOLO"],
    "YOLO": ["Detectron2"],
    "MediaPipe": ["Detectron2", "YOLO"],
    "OpenCV": ["scikit-image", "Pillow"],
    "Pillow": ["OpenCV", "scikit-image"],
    "scikit-image": ["OpenCV", "Pillow"],
    "MediaPipe": ["OpenCV", "Detectron2", "YOLO"],
    "Detectron2": ["YOLO", "OpenCV", "MediaPipe"],
    "YOLO": ["Detectron2", "OpenCV", "MediaPipe"],
    "Image Processing": ["OpenCV", "scikit-image", "Pillow"],
    "Computer Vision": ["OpenCV", "Detectron2", "YOLO", "MediaPipe"],

    # --- LLMs / AI ---
    "LLMs": ["Generative AI", "RAG", "Prompt Engineering"],
    "Generative AI": ["LLMs"],
    "RAG": ["LLMs"],
    "Prompt Engineering": ["LLMs"],

    # --- Time Series / Recommender Systems ---
    "Prophet": ["ARIMA", "tsfresh", "sktime"],
    "ARIMA": ["Prophet", "tsfresh", "sktime"],
    "tsfresh": ["Prophet", "ARIMA", "sktime"],
    "sktime": ["Prophet", "ARIMA", "tsfresh"],
    "Surprise": ["implicit"],
    "implicit": ["Surprise"],

    # --- Security ---
    "Firewall": ["IPS"],
    "Firewall Management": ["Firewall"],
    "Endpoint Security": ["Cybersecurity"],
    "IAM": ["Authentication Patterns"],
    "MFA": ["IAM"],
    "Cybersecurity": ["Endpoint Security", "Firewall", "IAM"],

    # --- Testing / QA ---
    "Software Testing": ["Quality Assurance", "Quality Control"],
    "Functional Testing": ["Manual Testing"],
    "Regression Testing": ["Functional Testing"],
    "Manual Testing": ["Functional Testing"],
    "Quality Assurance": ["Quality Control"],
    "Quality Control": ["Quality Assurance"],
    "Testing Library": ["Software Testing"],

    # --- Methodology ---
    "Agile": ["Scrum", "Kanban", "Extreme Programming (XP)", "Lean Software Development"],
    "Scrum": ["Kanban", "Agile"],
    "Kanban": ["Scrum", "Agile"],
    "Extreme Programming (XP)": ["Agile"],
    "Lean Software Development": ["Agile"],
    "Waterfall": ["V-Model", "Spiral Model"],
    "V-Model": ["Waterfall", "Spiral Model"],
    "Spiral Model": ["Waterfall", "V-Model"],

    # --- Office / Productivity ---
    "Microsoft Word": ["PowerPoint", "Excel"],
    "Excel": ["Microsoft Word", "PowerPoint"],
    "PowerPoint": ["Microsoft Word", "Excel"],
    "O365": ["Microsoft 365 Administration"],

    # --- IT / Infrastructure ---
    "Linux": ["Red Hat Enterprise Linux"],
    "Windows": ["Windows Server"],
    "Windows Server": ["Windows"],
    "Red Hat Enterprise Linux": ["Linux"],
}
