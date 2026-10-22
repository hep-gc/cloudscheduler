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
