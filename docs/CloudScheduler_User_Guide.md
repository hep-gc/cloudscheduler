# Cloud Scheduler User Guide

This guide explains what a user needs to do from the browser when the project starts empty and there are no cloud definitions yet. It is written as a practical operational guide for a real installation.

The most important point is this: Cloud Scheduler does not normally behave like a manual VM launcher. In this project, a user configures the environment and then lets the scheduler create VMs automatically when the HTCondor queue requires more resources.

## 1. What you need before Cloud Scheduler can start VMs

If the project is empty and there are no clouds configured, you need all of the following:

- a valid Cloud Scheduler server and browser access
- a valid user account
- an active group for the project
- a cloud definition for the target cloud backend
- valid cloud credentials and networking details
- a VM flavor / instance type that can run worker jobs
- metadata that contextualizes the VM as an HTCondor worker
- a queued HTCondor job to trigger the system

Without these, Cloud Scheduler has nothing to launch and nothing to scale.

## 2. Typical browser workflow for a new project

A normal start-up workflow is:

1. Log in to the Cloud Scheduler web application.
2. Select the project/group that owns the cloud resources.
3. Create the group if it does not already exist.
4. Create the cloud definition.
5. Enter cloud credentials and backend settings.
6. Configure metadata that bootstraps the VM as an HTCondor worker.
7. Queue a test HTCondor job.
8. Observe Cloud Scheduler creating VMs automatically.

## 3. Step 1: create or select the group

Cloud Scheduler is group-scoped. Most work is associated with a specific group.

In the browser:

- open the group pages
- create the group that will own the cloud resources
- choose the correct group as the active group

Once the group is active, the scheduler will treat that group as the owner of the cloud resources and job matching decisions.

If your project is new, this is the first operational step.

## 4. Step 2: create the cloud definition

Go to the cloud management page and create a cloud definition.

At minimum, the cloud definition needs to describe:

- the cloud type
- the authentication method
- the endpoint and region
- project / domain / tenant information if required
- credential details
- default networking and storage settings
- the available VM flavors

This is what allows Cloud Scheduler to talk to the actual cloud backend and create VMs there.

If the cloud definition is missing, the scheduler cannot launch anything.

## 5. Step 3: configure the worker metadata

This is the most important part for making the VM usable as an HTCondor worker.

A cloud-managed VM is not useful just because it exists in the cloud. It must be configured so that it becomes a real worker node. That is done through metadata.

In this project, metadata is a first-class concept. The code supports YAML-driven metadata and multi-part payloads for boot-time configuration. Those payloads are used to contextualize the VM at launch time.

In practical terms, this metadata should include:

- HTCondor configuration for the worker
- the collector or scheduler endpoint the worker should contact
- certificate/key material if the environment requires it
- any user-data or cloud-init style setup needed to prepare the machine
- any site-specific startup actions required for your project

Example intent:

- the VM boots
- cloud-init or equivalent user-data runs
- the node joins the HTCondor pool
- the worker is ready to run jobs

If this metadata is missing or incomplete, the VM may come up but will not behave as a functional worker node.

## 6. Step 4: set the VM flavor and resource limits

After the cloud definition exists, the system needs to know what kind of worker to start.

This includes:

- the flavor or instance type
- CPU and memory expectations
- disk size and swap settings if applicable
- limits on how many VMs can be started for the group/cloud combination

These are usually expressed as group or cloud configuration values and are part of the resource modeling used by the scheduler.

This matters because the backend decides how many VMs to start by comparing:

- the current job demand
- the active VM pool
- the available resources on the cloud
- the configured limit for that group/cloud

## 7. Step 5: queue a test HTCondor job

Once the group, cloud, and metadata are configured, the next step is to submit a simple HTCondor job.

This is the trigger that tells Cloud Scheduler to scale the VM pool.

The scheduler checks:

- whether there are idle jobs
- whether the group has enough active resources
- whether there is cloud capacity available
- whether starting one or more VMs will satisfy the shortfall

If the queue indicates demand, Cloud Scheduler starts additional VMs automatically.

## 8. Step 6: let the scheduler scale the VM pool

This is the core operational model of the system.

When a group has queued jobs that cannot be satisfied by the current pool, the backend logic does the following:

1. checks the idle-job view
2. calculates the shortfall in CPU, RAM, and disk
3. evaluates cloud capacity and VM flavor availability
4. selects the appropriate cloud
5. throttles the number of new VMs based on configured limits
6. launches the needed VMs
7. waits for them to contextualize and join HTCondor
8. runs the queued jobs when the resources are available

This is the automatic VM scaling pattern in Cloud Scheduler.

## 9. What the user is expected to do in practice

For a new installation, the expected browser workflow is not to manually create a VM and then attach it to HTCondor by hand. Instead, the intended workflow is:

- create the group
- create the cloud definition
- configure cloud metadata
- submit a job
- watch the VM list and job list as Cloud Scheduler creates and provisions workers automatically

The user is acting as the operator who configures the environment and monitors it, while the scheduler does the resource matching and VM creation.

## 10. What must be true for end-to-end success

For Cloud Scheduler to work end-to-end, all of the following must be valid:

- the Cloud Scheduler server is running and reachable
- the user is authenticated and has the required rights
- the active group is correct
- the cloud definition is complete and valid
- the cloud backend accepts VM creation requests
- the worker metadata correctly configures the node as an HTCondor worker
- the group has enough VM and resource limits configured
- there is HTCondor work waiting in the queue

If any of these are missing, the VM pool will not start or will not become usable.

## 11. What to monitor in the browser

After the initial setup, the normal operational view is:

- cloud status
- cloud list
- VM list
- job list
- group metadata
- cloud metadata

The user should watch these pages to confirm that:

- the cloud is healthy
- the VM pool is growing when jobs are queued
- the VMs are launched on the expected cloud
- the VMs are contextualized correctly
- the queued jobs are eventually running

## 12. Summary

If there are no clouds configured yet, the user must first create a valid group and cloud definition. The next critical step is metadata, because that is how a new machine is contextualized as an HTCondor worker. After that, the user submits a job and lets Cloud Scheduler react by automatically starting VMs as demand appears in the HTCondor queue.

In short, the real workflow is:

- configure group + cloud + metadata
- queue work
- let the backend auto-scale the VM pool
- verify the workers join HTCondor and run jobs

This is the practical browser-based use model of Cloud Scheduler in this repository.

## 13. CLI equivalent: how to do the same steps from the command line

The CLI uses the same model as the browser, but through the `cloudscheduler` command. The commands map to the same underlying operations: group setup, cloud definition, metadata, and job/VM monitoring.

### 13.1 Set up the server profile

First define a saved server profile:

```bash
cloudscheduler defaults set -s prod
```

Then set the server address and credentials:

```bash
cloudscheduler defaults set -s prod -sa https://cloudscheduler.example.org -su myuser -spw mypassword
```

If the installation uses certificate-based authentication instead of username/password:

```bash
cloudscheduler defaults set -s prod -sa https://cloudscheduler.example.org -x509
```

### 13.2 Select the active group

Set the default group for the current user:

```bash
cloudscheduler my settings -gn mygroup
```

You can confirm your current settings:

```bash
cloudscheduler my settings
```

### 13.3 Create or review group definitions

List existing groups:

```bash
cloudscheduler group list
```

Create or update a group as needed using the group commands.

### 13.4 Create or review cloud definitions

List configured clouds:

```bash
cloudscheduler cloud list
```

Add or update a cloud definition:

```bash
cloudscheduler cloud add
cloudscheduler cloud update
```

Check cloud status:

```bash
cloudscheduler cloud status
```

### 13.5 Configure metadata for worker bootstrapping

List metadata:

```bash
cloudscheduler metadata list
```

Load or update metadata definitions that will be used as part of the group or cloud configuration:

```bash
cloudscheduler metadata load
cloudscheduler metadata update
```

This is the CLI equivalent of setting the metadata that contextualizes a VM as an HTCondor worker.

### 13.6 Queue a test job

Once the group and cloud are configured, submit or inspect jobs:

```bash
cloudscheduler job list
```

From the HTCondor side, the important thing is that the queue is populated with jobs for the same group and resource policy that Cloud Scheduler is monitoring.

### 13.7 Let the backend scale the VM pool

After the job is queued, the scheduler loop monitors the idle jobs and available resources, and then creates VMs automatically if there is a shortfall. The CLI is used to observe that state, not to manually create workers one by one.

Useful checks:

```bash
cloudscheduler cloud status
cloudscheduler vm list
cloudscheduler job list
cloudscheduler group list
```

### 13.8 CLI summary

The CLI equivalent of the browser workflow is:

```bash
cloudscheduler defaults set -s prod -sa https://cloudscheduler.example.org -su myuser -spw mypassword
cloudscheduler my settings -gn mygroup
cloudscheduler group list
cloudscheduler cloud add
cloudscheduler cloud status
cloudscheduler metadata list
cloudscheduler job list
cloudscheduler vm list
```

This mirrors the browser workflow:

- configure the server
- select the group
- create or validate the cloud definition
- add metadata for worker bootstrapping
- queue work
- watch Cloud Scheduler start the required VMs and run HTCondor jobs

## 14. Browser vs CLI: the same model

The browser and the CLI are two interfaces to the same Cloud Scheduler operational model.

In both cases the flow is the same:

- create the project group
- define the cloud
- configure metadata so the VM becomes a proper worker
- allow queued jobs to trigger VM creation
- monitor cloud, VM, and job state
- let the scheduler handle the scaling automatically

The browser is easier for most operators to use interactively; the CLI is useful for scripted administration and repeatable setup.
