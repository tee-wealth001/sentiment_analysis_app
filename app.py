import pandas as pd
import numpy as np
import re
import streamlit as st
import nltk
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

import contractions

from dotenv import load_dotenv
import os
from llm_entity import TASK_LLM
from langchain.prompts import PromptTemplate
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="Build Your Sentiment Classification Pipeline", layout="wide")

@st.cache_resource
def load_model():
    return TASK_LLM  # Load LLM only once

#Css styles
def load_css():
    st.markdown(
        """
<style>
/* Global Styles */


/* Title and Header Styles */
.stTitle {
    color: #4CAF50 !important;
    font-size: 3rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

h1 {
    color: #4CAF50 !important;
}

/* Sidebar Styles */
.css-1d391kg {
    background-color: #2d2d2d;
    padding: 2rem 1rem;
    border-right: 1px solid #3d3d3d;
}

.sidebar .stButton > button {
    width: 100%;
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 0.75rem;
    border-radius: 5px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.sidebar .stButton > button:hover {
    background-color: #45a049;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Job Card Styles */
.job-card {
    background-color: #2d2d2d;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.job-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.2);
}

/* Button Styles */
.stButton > button {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background-color: #45a049;
    transform: translateY(-2px);
}

/* Analysis Panel Styles */
.fixed-analysis {
    border-left: 1px solid #3d3d3d !important;
    padding: 2rem !important;
    box-shadow: -4px 0 8px rgba(0,0,0,0.1);
}

.fixed-analysis h3 {
    color: #4CAF50;
    margin-bottom: 1rem;
}

/* File Uploader Styles */
.stFileUploader {
    border-radius: 8px;
    padding: 1rem;
    border: 2px dashed #4CAF50;
}

/* Pagination Styles */
.pagination {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin: 2rem 0;
}

.pagination button {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.3s ease;
}

/* Link Button Styles */
.stLinkButton > button {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stLinkButton > button:hover {
    background-color: #1976D2;
    transform: translateY(-2px);
}

/* Loading Spinner Styles */
.stSpinner {
    color: #4CAF50 !important;
}

/* Alert/Warning Styles */
.stAlert {
    border-radius: 5px;
    border-left: 4px solid #0abb59;
}

/* Success Message Styles */
.success-message {
    background-color: rgba(76, 175, 80, 0.1);
    border-left: 4px solid #4CAF50;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}

/* Error Message Styles */
.error-message {
    background-color: rgba(244, 67, 54, 0.1);
    border-left: 4px solid #f44336;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}

/* Caption Styles */
.stCaption {
    color: #999;
    font-size: 0.9rem;
}

/* Divider Styles */
.stDivider {
    border-color: #3d3d3d;
    margin: 2rem 0;
}

/* Responsive Design */
@media (max-width: 768px) {
    .fixed-analysis {
        position: relative !important;
        width: 100% !important;
        margin-top: 2rem;
    }
    
    .stTitle {
        font-size: 2rem;
    }
}
</style>
    """,
        unsafe_allow_html=True,
    )


# Load environment variables
load_dotenv()
huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Download NLTK data
# nltk.download("punkt")
# nltk.download("stopwords")
# nltk.download("wordnet")

# Custom CSS for styling the Streamlit app
st.markdown(
    """
    <style>
    /* Style the sidebar */

    /* Style the buttons */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 8px;
        border: none;
        font-size: 16px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }

    /* Style the DataFrame display */
    .stDataFrame {
        border-radius: 8px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    }

    /* Customize text and font */
    body {
        font-family: 'Arial', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


analyzer = SentimentIntensityAnalyzer()


# Function to preprocess text
def preprocess_text(text, steps):
    if "Convert to lowercase" in steps:
        text = text.lower()
    if "Remove punctuation" in steps:
        text = re.sub(r"[^\w\s]", "", text)
    if "Remove URLs" in steps:
        text = re.sub(r"http\S+", "", text)
    if "Remove Mentions" in steps:
        text = re.sub(r"@\w+", "", text)
    if "Remove Hashtags" in steps:
        text = re.sub(r"#\w+", "", text)
    if "Remove Non-Alphabetic" in steps:
        text = re.sub(r"[^a-zA-Z\s]", "", text)
    if "Expand Contractions" in steps:
        text = contractions.fix(text)
    if "Remove Emojis" in steps:
        text = text.encode("ascii", "ignore").decode("ascii")
    tokens = word_tokenize(text)
    if "Remove stopwords" in steps:
        stop_words = set(stopwords.words("english"))
        tokens = [word for word in tokens if word not in stop_words]
    if "Lemmatize words" in steps:
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
    text = " ".join(tokens)
    if "Stem words" in steps:
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(word) for word in tokens]
    if "Remove Extra Whitespaces" in steps:
        text = re.sub(r"\s+", " ", text).strip()
    return text


def assign_sentiment(text, method="vader"):
    if method == "vader":
        score = analyzer.polarity_scores(text)["compound"]
        # Return 1 for positive, 0 for negative
        return 1 if score > 0.05 else 0

    elif method == "textblob":
        score = TextBlob(text).sentiment.polarity
        # Return 1 for positive, 0 for negative
        return 1 if score > 0 else 0


# Function to analyze results with LLM
def analyze_with_llm(results):
    """
    Sends the results to a Hugging Face LLM for analysis and feedback.
    """
    formatted_results = "\n".join(
        [
            f"Classifier: {name}\n"
            + "\n".join(
                [
                    (
                        f"{metric}: {value:.2f}"
                        if isinstance(value, (int, float))
                        else f"{metric}:\n{value}"
                    )
                    for metric, value in metrics.items()
                ]
            )
            for name, metrics in results.items()
        ]
    )

    # Define the prompt for the LLM
    prompt = f"""
    You are an expert in machine learning and model evaluation. 
    Please analyze the following classification results and provide insights:
    
    {formatted_results}
    
    Highlight any potential improvements or issues with the results.
    """

    prompt_template = PromptTemplate(
        template=prompt,
        input_variables=["formatted_results"],
    )
    question_generator = prompt_template | load_model()
    result = question_generator.invoke(
        {
            "context": formatted_results,
        }
    )
    return result.content


# Function to display the DataFrame with the selected columns
def write_to_df():
    if "sentiment" not in data.columns:
        # data["sentiment"] = data[column_to_preprocess].apply(
        #     lambda x: assign_sentiment(x, selected_classifiers[0])
        st.dataframe(
            data[[column_to_preprocess, "preprocessed_text"]]
        )  # Display three columns
    else:
        st.dataframe(data[[column_to_preprocess, "preprocessed_text", "sentiment"]])


# This function takes the confusion matrix (cm) from the cell above and produces all evaluation matrix
def confusion_metrics(conf_matrix):

    TP = conf_matrix[1][1]
    TN = conf_matrix[0][0]
    FP = conf_matrix[0][1]
    FN = conf_matrix[1][0]
    st.write("True Positives:", TP)
    st.write("True Negatives:", TN)
    st.write("False Positives:", FP)
    st.write("False Negatives:", FN)

    # calculate accuracy
    conf_accuracy = float(TP + TN) / float(TP + TN + FP + FN)

    # calculate mis-classification
    conf_misclassification = 1 - conf_accuracy

    # calculate the sensitivity
    conf_sensitivity = TP / float(TP + FN)
    # calculate the specificity
    conf_specificity = TN / float(TN + FP)

    # calculate precision
    conf_precision = TN / float(TN + FP)
    # calculate f_1 score
    conf_f1 = 2 * (
        (conf_precision * conf_sensitivity) / (conf_precision + conf_sensitivity)
    )
    st.write(f"Mis-Classification: {round(conf_misclassification,2)}")
    st.write(f"Sensitivity: {round(conf_sensitivity,2)}")
    st.write(f"Specificity: {round(conf_specificity,2)}")
    st.write(f"Precision: {round(conf_precision,2)}")
    st.write(f"f_1 Score: {round(conf_f1,2)}")
    st.write("-" * 50)


# Sidebar for inputs
st.sidebar.title("Build Your Sentiment Classification Pipeline")
# uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# # Column selection for preprocessing
# column_to_preprocess = None
isCustomAnalyzer = False


# # Check if a file is uploaded
# if uploaded_file:
#     st.write("### Dataset Uploaded")
#     print("begining here")
#     data = pd.read_csv(uploaded_file)
#     if "sentiment" not in data.columns:
#         st.warning("The CSV file must contain a 'sentiment' column.")
#         isCustomAnalyzer = True
#     else:
#         isCustomAnalyzer = False
# At the start of your script, define all the session state variables that need to be reset
def reset_session_state():
    session_states = [
        "uploaded_data",
        "preprocessed_data",
        "sentiment_data",
        "preprocessing_steps_selected",
        "selected_analyzer",
        "results",
    ]
    for state in session_states:
        if state in st.session_state:
            del st.session_state[state]


# Modify your file uploader section
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# Check if a file is uploaded
if uploaded_file:
    # Get the name of the currently uploaded file
    file_name = uploaded_file.name

    # Check if this is a new file
    if (
        "current_file" not in st.session_state
        or st.session_state["current_file"] != file_name
    ):
        # Reset everything if it's a new file
        reset_session_state()
        st.session_state["current_file"] = file_name

    st.write("### Dataset Uploaded")
    data = pd.read_csv(uploaded_file)
    # Check for null values
    if data.isnull().values.any():
        remove_na = st.sidebar.checkbox("Remove NaN values")
        if remove_na:
            data = data.dropna()

    if "sentiment" not in data.columns:
        st.warning("The CSV file must contain a 'sentiment' column.")
        isCustomAnalyzer = True
    else:
        isCustomAnalyzer = False

    st.sidebar.write("### Select the Column to Preprocess")
    column_to_preprocess = st.sidebar.selectbox(
        "Select the column to preprocess:", data.columns
    )

    # Preprocessing options in the sidebar
    preprocessing_steps = st.sidebar.multiselect(
        "Choose preprocessing steps:",
        [
            "Convert to lowercase",
            "Remove punctuation",
            "Remove URLs",
            "Remove Mentions",
            "Remove Hashtags",
            "Remove Non-Alphabetic",
            "Expand Contractions",
            "Remove Emojis",
            "Remove stopwords",
            "Lemmatize words",
            "Stem words",
            "Remove Extra Whitespaces",
        ],
    )

    # Preprocessing button in the sidebar
    preprocess_btn = st.sidebar.button("Apply Preprocessing")

    # Custom analyzer options in the sidebar
    if isCustomAnalyzer:
        st.sidebar.write("### Generate Sentiment with Custom Analyzer")
        selected_analyzer = st.sidebar.selectbox(
            "Choose analyzer:",
            [
                "vader",
                "textblob",
            ],
        )

        # Custom analyzer button in the sidebar
        custom_analyzer_btn = st.sidebar.button("Generate Sentiment")

    # Classifier and metrics options in the sidebar
    st.sidebar.write("### Select Classifiers and Metrics")
    selected_classifiers = st.sidebar.multiselect(
        "Choose classifiers:",
        [
            "Logistic Regression",
            "Naive Bayes",
            "Support Vector Machine",
            "Random Forest",
            "Gradient Boosting",
        ],
    )

    # Metrics selection in the sidebar
    metrics = st.sidebar.multiselect(
        "Choose metrics to evaluate your model:",
        ["Accuracy", "Precision", "Recall", "F1 Score", "Confusion Matrix"],
    )

    # Run pipeline button in the sidebar
    pipeline_btn = st.sidebar.button("Run Pipeline")

    # Analyze with LLM button in the sidebar
    analyze_with_llm_btn = st.sidebar.button("Analyze Results with LLM", disabled=True)

# Initialize session state if not already initialized
if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = None
if "preprocessed_data" not in st.session_state:
    st.session_state["preprocessed_data"] = None
if "sentiment_data" not in st.session_state:
    st.session_state["sentiment_data"] = None
if "preprocessing_steps_selected" not in st.session_state:
    st.session_state["preprocessing_steps_selected"] = ""
if "selected_analyzer" not in st.session_state:
    st.session_state["selected_analyzer"] = ""
if "results" not in st.session_state:
    st.session_state["results"] = {}


# Only proceed if a file is uploaded
if uploaded_file:
    # Load dataset
    st.session_state["uploaded_data"] = data  # Store uploaded data in session state
    st.write("### Dataset Preview")
    st.write(data.head())

    # if "sentiment" not in data.columns:
    #     st.warning("The CSV file must contain a 'sentiment' column.")
    # else:
    # Main content area
    st.title("Sentiment Classification Pipeline")

    # Display the preprocessing table if preprocessed data exists
    if st.session_state["preprocessed_data"] is not None:
        # Add preprocessed data as a new column in the DataFrame
        data["preprocessed_text"] = st.session_state["preprocessed_data"]
        st.write("### Preprocessed Data Preview")
        write_to_df()

    if st.session_state["sentiment_data"] is not None:
        # Add preprocessed data as a new column in the DataFrame
        data["sentiment"] = st.session_state["sentiment_data"]
        st.write("### Sentiment Data Preview")
        write_to_df()

    # Apply preprocessing when button clicked
    if preprocess_btn:
        with st.spinner("Preprocessing... Please wait."):
            if not preprocessing_steps:
                st.warning(
                    "No preprocessing steps selected. The raw text will be used."
                )
                st.session_state["preprocessed_data"] = data[column_to_preprocess]
            else:
                st.write("### Preprocessing Data...")
                # Apply preprocessing and store as a new column
                st.session_state["preprocessed_data"] = data[
                    column_to_preprocess
                ].apply(lambda x: preprocess_text(x, preprocessing_steps))
            # Display the new column in the data
            data["preprocessed_text"] = st.session_state["preprocessed_data"]
            write_to_df()

    # Generate sentiment with custom analyzer when button clicked
    if isCustomAnalyzer:
        if custom_analyzer_btn:
            # Check if the button is clicked
            with st.spinner("Generating sentiment... Please wait."):
                if not selected_analyzer:
                    st.warning(
                        "No analyzer selected. Please select at least one analyzer."
                    )
                else:
                    st.write("### Generating Sentiment with Custom Analyzer...")
                    # st.session_state["sentiment_data"] = data["preprocessed_text"].apply(
                    #     lambda x: assign_sentiment(x, selected_analyzer)
                    # )
                    st.session_state["sentiment_data"] = data[
                        "preprocessed_text"
                    ].apply(assign_sentiment, method=selected_analyzer)
                    # Add sentiment as a new column in the DataFrame
                    data["sentiment"] = st.session_state["sentiment_data"]
                    st.session_state["uploaded_data"] = (
                        data  # Store updated data in session state
                    )
                    write_to_df()

    if "sentiment" in data.columns:
        # Ensure preprocessed data is available before using it in train_test_split
        if st.session_state["preprocessed_data"] is not None:
            X = st.session_state["preprocessed_data"]
            y = data["sentiment"]
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            if pipeline_btn:
                with st.spinner("Training and evaluating models... Please wait."):
                    if not selected_classifiers:
                        st.warning(
                            "No classifiers selected. Please select at least one classifier."
                        )
                    elif not metrics:
                        st.warning(
                            "No metrics selected. Please select at least one evaluation metric."
                        )
                    else:
                        st.write("### Training and Evaluating Models...")
                        classifiers = {
                            "Logistic Regression": LogisticRegression(),
                            "Naive Bayes": MultinomialNB(),
                            "Support Vector Machine": SVC(),
                            "Random Forest": RandomForestClassifier(),
                            "Gradient Boosting": GradientBoostingClassifier(),
                        }
                        results = {}  # Initialize results
                        y_preds = {}

                        # Train and predict for each selected classifier
                        for name in selected_classifiers:
                            classifier = classifiers[name]
                            pipeline = Pipeline(
                                [("tfidf", TfidfVectorizer()), ("clf", classifier)]
                            )
                            pipeline.fit(X_train, y_train)
                            y_pred = pipeline.predict(X_test)

                            # Store the predictions for later use in confusion matrix plotting
                            y_preds[name] = y_pred

                            # Calculate metrics
                            model_metrics = {}
                            if "Accuracy" in metrics:
                                model_metrics["Accuracy"] = accuracy_score(
                                    y_test, y_pred
                                )
                            if "Precision" in metrics:
                                model_metrics["Precision"] = precision_score(
                                    y_test, y_pred, average="weighted"
                                )
                            if "Recall" in metrics:
                                model_metrics["Recall"] = recall_score(
                                    y_test, y_pred, average="weighted"
                                )
                            if "F1 Score" in metrics:
                                model_metrics["F1 Score"] = f1_score(
                                    y_test, y_pred, average="weighted"
                                )

                            # Include confusion matrix in results if selected
                            if "Confusion Matrix" in metrics:
                                cm = confusion_matrix(y_test, y_pred)
                                model_metrics["Confusion Matrix"] = cm.tolist()

                            results[name] = model_metrics

                        # Save results in session state
                        st.session_state["results"] = results

                        # Display results
                        st.write(f"## Metrics Results")
                        for name, model_metrics in results.items():
                            st.write(f"### {name}")
                            for metric_name, metric_value in model_metrics.items():
                                if metric_name != "Confusion Matrix":
                                    st.write(
                                        f"**{metric_name}:** {metric_value:.2f}"
                                    )  # Only format numerical values

                        # Plot confusion matrices for each selected classifier
                        if "Confusion Matrix" in metrics:
                            st.write(f"## Confusion Matrix Plot")
                            for name, y_pred in y_preds.items():
                                cm = confusion_matrix(y_test, y_pred)
                                disp = ConfusionMatrixDisplay(
                                    confusion_matrix=cm,
                                    display_labels=["Negative", "Positive"],
                                )
                                disp.plot(cmap=plt.cm.Blues)
                                plt.title(f"Confusion Matrix: {name}")
                                st.pyplot(plt.gcf())
                                plt.clf()  # Clear the current figure to avoid overlap in next plot
                                st.write(f"**{name}:** \n")
                                confusion_metrics(cm)
                        # # Plot confusion matrices for each selected classifier
                        # if "Confusion Matrix" in metrics:
                        #     st.write(f"## Confusion Matrix Plot")
                        #     for name, y_pred in y_preds.items():
                        #         cm = confusion_matrix(y_test, y_pred)
                        #         # Get unique labels from the data
                        #         unique_labels = sorted(np.unique(np.concatenate([y_test, y_pred])))

                        #         disp = ConfusionMatrixDisplay(
                        #             confusion_matrix=cm,
                        #             display_labels=unique_labels
                        #         )
                        #         fig, ax = plt.subplots()
                        #         disp.plot(ax=ax, cmap=plt.cm.Blues)
                        #         plt.title(f"Confusion Matrix: {name}")
                        #         st.pyplot(fig)
                        #         plt.close(fig)

    # Add the button to the sidebar
    if analyze_with_llm_btn:
        # Check if results are available in session state
        if "results" in st.session_state and st.session_state["results"]:
            with st.spinner("Analyzing results with LLM..."):
                try:
                    llm_analysis = analyze_with_llm(st.session_state["results"])
                    st.write("### LLM Analysis of Results")
                    st.write(llm_analysis)
                except Exception as e:
                    st.error(f"An error occurred while analyzing with LLM: {e}")
        else:
            st.warning("No results available to analyze. Run the pipeline first.")

    load_css()

