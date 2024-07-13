import boto3
import os
import subprocess

def run_command(command):
    """Run a system command and return its output, error and status code."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode('utf-8'), error.decode('utf-8'), process.returncode

def describe_cluster(eks_client, cluster_name):
    """Describe the EKS cluster."""
    response = eks_client.describe_cluster(name=cluster_name)
    return response

def update_kubeconfig(cluster_name):
    """Update kubeconfig for kubectl to interact with the EKS cluster."""
    output, error, status = run_command(f'aws eks update-kubeconfig --name {cluster_name}')
    return status

def get_pods(namespace):
    """Get the list of pods in the specified namespace."""
    output, error, status = run_command(f'kubectl get pods -n {namespace}')
    return output, status

def describe_pod(pod_name, namespace):
    """Describe a specific pod."""
    output, error, status = run_command(f'kubectl describe pod {pod_name} -n {namespace}')
    return status

def get_pod_logs(pod_name, namespace):
    """Get logs of a specific pod."""
    output, error, status = run_command(f'kubectl logs {pod_name} -n {namespace}')
    return status

def test_networking(pod_name, namespace, test_url):
    """Test networking from a pod by curling a test URL."""
    command = f'kubectl exec {pod_name} -n {namespace} -- curl -s -o /dev/null -w "%{{http_code}}" {test_url}'
    output, error, status = run_command(command)
    return status

def main():
    cluster_name = 'my-eks-cluster'
    namespace = 'default'
    test_url = 'https://www.google.com'
    
    # Initialize boto3 client
    eks_client = boto3.client('eks')

    # describe EKS 
    cluster_response = describe_cluster(eks_client, cluster_name)
    print("Cluster Description Status Code:", cluster_response['ResponseMetadata']['HTTPStatusCode'])
    
    # kubeconfig
    kubeconfig_status = update_kubeconfig(cluster_name)
    print("Update Kubeconfig Status Code:", kubeconfig_status)

    # wp Pods
    pods_output, pods_status = get_pods(namespace)
    print("Get Pods Status Code:", pods_status)
    
    if pods_status != 0:
        print("Failed to get pods. Exiting.")
        return

    # Parse pod names from output
    pod_names = [line.split()[0] for line in pods_output.split('\n')[1:] if line]
    
    for pod_name in pod_names:
        # Describe each pod
        describe_status = describe_pod(pod_name, namespace)
        print(f"Describe Pod {pod_name} Status Code:", describe_status)

        # Get logs for each pod
        logs_status = get_pod_logs(pod_name, namespace)
        print(f"Logs for Pod {pod_name} Status Code:", logs_status)
        


if __name__ == "__main__":
    main()
