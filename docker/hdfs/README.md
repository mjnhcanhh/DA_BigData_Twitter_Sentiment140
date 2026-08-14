# HDFS local cluster

This optional Docker Compose stack runs one HDFS NameNode and one DataNode for coursework
demonstration. It uses the Apache Software Foundation `apache/hadoop:3.3.6` image and keeps
NameNode/DataNode state in named Docker volumes.

- NameNode RPC for the host Spark client: `hdfs://localhost:8020`
- NameNode web interface: <http://localhost:9870>
- DataNode web interface: <http://localhost:9864>
- Replication factor: 1 (because this is a one-DataNode local lab)
- HDFS block size: 128 MiB

Use the PowerShell scripts in `scripts/` instead of invoking this file manually. `hdfs_stop.ps1`
does not delete named volumes, so HDFS data remains available after restarting the containers.

