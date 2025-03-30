import os
from google.cloud import aiplatform

# Configuration (replace with your actual project details)
PROJECT_ID = "timekeeper-455221"
LOCATION = "us-central1"  # e.g., us-central1


def test_vertex_connection():
    """
    Initializes the Vertex AI client and lists available endpoints
    to verify connection and authentication.
    """
    print(
        f"Attempting to connect to Vertex AI project: {PROJECT_ID} in location: {LOCATION}"
    )
    try:
        # Initialize the Vertex AI client.
        # ADC should automatically find the credentials configured earlier
        # via 'gcloud auth application-default login'.
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        print("Vertex AI client initialized successfully.")

        # List endpoints as a simple test call
        print("\nListing first few Vertex AI Endpoints:")
        endpoints = aiplatform.Endpoint.list(order_by="create_time desc")

        count = 0
        for endpoint in endpoints:
            print(
                f"- Endpoint ID: {endpoint.name}, Display Name: {endpoint.display_name}"
            )
            count += 1
            if count >= 5:  # List only the first 5 for brevity
                break

        if count == 0:
            print("No endpoints found in this project/location.")
        else:
            print(f"\nListed {count} endpoint(s).")

        print("\nConnection test successful!")

    except ImportError as e:
        print(f"\nError: {e}")
        print(
            "It seems the 'google-cloud-aiplatform' library might not be installed correctly."
        )
        print(
            "Try running 'hatch run pip install -e .[dev,docs]' within the hatch shell and then run this script again."
        )
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print(
            "Please check your GCP project ID, location, and authentication setup (ADC)."
        )
        print(
            "Ensure the Vertex AI API is enabled for your project."
        )  # billingbudgets API was enabled, but maybe not aiplatform?


if __name__ == "__main__":
    test_vertex_connection()
