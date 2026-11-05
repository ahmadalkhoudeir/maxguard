@load protocols/conn/known-hosts
@load protocols/conn/known-services
@load frameworks/software/version-changes

redef Known::host_tracking = ALL_HOSTS;
redef Known::service_tracking = ALL_HOSTS;
redef Software::asset_tracking = ALL_HOSTS;
