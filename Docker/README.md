# VSR_Autoscaler
Container ready version of the script. Uses Env variables instead of cmd line args.

## example
1. Build the image 
`Docker build -t vsrautoscaler /app/Docker`
1. Run 
`Docker run -it vsrautoscaler -e RefreshToken=11670dd3-ba77-48e8-8086-b33e58b0e0cc -e OrgID=194734cc-fbc1-4b72-9090-2523d8522148 -e SddcID=abd3761a-8730-400a-95cb-f86820169f7c -e ClusterName=Cluster-1 -e ClusterSize=5 -e DRNetwork=10.72.30.0/24`
