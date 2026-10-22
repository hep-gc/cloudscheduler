# Cloud Scheduler User Guide

This guide explains how a user actually works with Cloud Scheduler after the system is installed. It focuses on the browser workflow and on how VMs are started from HTCondor queue demand.

Cloud Scheduler is not a standalone local scheduler. It is a server-backed system. The browser and CLI are both front ends to a running Cloud Scheduler service. The real work happens in the backend: the server stores the group, cloud, VM, and job state; the scheduler logic decides when more VMs are needed; and the cloud backend creates or terminates VMs accordingly.

## 1. What a user does after logging in

After opening the Cloud Scheduler web UI, the normal user workflow is:

1. select the correct server and user session
2. choose the active group
3. review cloud definitions
4. check VM state and jobs
5. edit or review metadata that determines how worker VMs are configured
6. let the backend create VMs automatically as workload requires

The most important point is that users do not usually create VMs manually one by one. In this system, the typical flow is to define the cloud, define the group defaults and metadata, queue jobs, and let the scheduler start VMs automatically when the HTCondor queue indicates demand.

## 2. Browser workflow: a practical day-to-day pattern

A typical browser-based user flow is:

- Open the Cloud Scheduler web application.
- Select the active group for the project or team.
- Review the list of cloud definitions.
- Confirm that the correct cloud backend is enabled.
- Review the group metadata and cloud metadata.
- Check the VM list and the job list.
- Let the backend start or retire VMs as needed.

The role of the browser is mostly configuration, monitoring, and operational oversight. The actual VM scaling decisions are made by the backend scheduler, driven by job demand and resource availability.

## 3. How VM auto-scaling works from the HTCondor queue

This is the core behavior of Cloud Scheduler in this repository.

The scheduler loop is in the backend service (`cloudscheduler/csmain`). It periodically does the following:

- reads the current queue and job state
- looks for idle jobs
- checks which groups have jobs waiting but not enough active resources
- checks which clouds and flavors have capacity available
- computes the shortfall in CPU, RAM, and disk
- calculates how many VMs are required to satisfy the queue demand
- boots VMs on the appropriate cloud

The code looks at the idle-job view and resource views, then evaluates shortfall values such as:

- shortfall_cores
- shortfall_disk
- shortfall_ram

It also checks available capacity through the resource model and keeps some throttling in place so that it does not flood a cloud with too many new VMs at once.

In real terms, the flow is:

1. HTCondor reports that jobs are idle or waiting for resources.
2. Cloud Scheduler checks whether the group has enough active VMs to satisfy the demand.
3. If active resources are below the required threshold, the scheduler finds a suitable cloud/flavor.
4. It decides how many VMs are needed.
5. It boots new VMs on the cloud.
6. The newly started VMs register themselves and begin accepting HTCondor work.

This is why the system behaves as a dynamic cloud worker pool: the queue drives the need, and the backend creates VMs to match that workload.

## 4. Why the queue matters

The queue is not just a list of tasks. In Cloud Scheduler, it is effectively the trigger that tells the system it needs more capacity.

The backend checks for:

- groups with idle jobs
- jobs that cannot run because there are not enough resources available
- resource shortfall in the current group/cloud combination
- cloud capacity and policy limits

When those conditions are met, the scheduler decides to start VMs automatically.

The user experience is therefore:

- queue work
- monitor the VM list
- see new worker VMs appear when demand increases
- see VMs retire or terminate when they are no longer needed

## 5. How VM contextualization is configured

Contextualization is how a VM becomes a working HTCondor worker after it starts. The repository contains the cloud-init and metadata tooling for this.

The code in `cloudscheduler/cloud_init_util.py` shows that Cloud Scheduler can construct multi-part metadata payloads from YAML snippets and file content. The system supports:

- YAML content
- MIME-typed data attachments
- cloud-init style files
- user-data payloads that are attached to the VM at boot time

In practical terms, this is where the user defines how each VM should configure itself once it boots. This can include:

- system configuration
- package installation
- user setup
- HTCondor worker configuration
- certificates or keys
- cloud-specific bootstrap actions

The metadata is attached to the group or cloud configuration that the scheduler uses when it launches new VMs. Once the VM boots, the metadata is applied and the machine becomes a working job-execution node.

This is the crucial difference between “a VM exists in the cloud” and “a VM is usable as a Cloud Scheduler worker.” The second part comes from contextualization.

## 6. What a user configures in the browser to enable this

To enable automatic VM startup from queued work, a user typically configures the following in the browser:

- the correct group context
- the relevant cloud definition
- the endpoint credentials and region
- cloud metadata and defaults
- worker-related metadata values used at boot time
- the VM flavor or instance type that should be launched for that group

This is the operational setup that turns a cloud into a usable worker pool.

The browser does not usually replace the scheduler logic; it supplies the information the backend needs to make the right decision.

## 7. Common admin workflow in the browser

A common admin workflow is:

1. Log in to the Cloud Scheduler web interface.
2. Pick the project or group that owns the worker pool.
3. Review or create the cloud definition.
4. Confirm authentication, region, project, and network settings.
5. Define or update cloud metadata, including any worker bootstrap configuration.
6. Review the available VM flavors and limits for the group.
7. Ensure the group has the right metadata defaults.
8. Open the VM and job views to monitor activity.
9. Watch the system auto-create VMs when the queue shows idle demand.
10. Terminate or retire VMs when load drops or they are no longer needed.

This is the normal operational model: configure the environment, queue jobs, and let Cloud Scheduler scale the VM pool up and down based on the HTCondor queue and resource constraints.

## 8. What to monitor as a user

A normal operator should monitor these items:

- cloud status
- cloud list
- VM list
- job list
- group metadata
- VM contextualization metadata
- VM retirement or termination events

The purpose is to make sure that queued jobs are matched by sufficient cloud capacity and that started VMs are correctly configured to join the HTCondor pool.

## 9. Typical operator mental model

The real mental model is:

- The queue says “we need more workers.”
- The scheduler checks whether the current group/cloud has enough active capacity.
- If not, it prepares to launch more VMs.
- The cloud metadata and boot configuration make the new VM join the worker pool correctly.
- The browser is used to configure and observe this process.

This is more like an elastic cloud worker system than a manual VM-start process.

## 10. Summary

A user is expected to work with Cloud Scheduler in the browser by:

- selecting the correct group
- defining the cloud and credentials
- setting metadata and defaults
- monitoring VM and job state
- letting the scheduler auto-start VMs based on HTCondor queue demand

The automatic VM scaling is driven by queue demand and resource shortfall, while VM preparation depends on metadata and contextualization at boot time.

That is the real operational pattern for using Cloud Scheduler once it is installed.
