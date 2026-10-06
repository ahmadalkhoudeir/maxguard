##! Live sensor log rotation (Jakub, JAK-07).
##!
##! Zeek writes the logs of the interval in progress into its working folder
##! (/data/spool/zeek in docker/sensor-compose.yaml). At the end of every
##! interval it closes them and moves them into one folder per interval:
##!
##!     /data/zeek/2026-10-06-1415/conn.log, dns.log, http.log, ...
##!
##! The folder is named after the interval's START, in UTC (the container runs
##! with TZ=UTC). The files keep their plain names, so a finished folder is an
##! ordinary Zeek log folder that MaxGuard can analyze or ship as it is.
##!
##! No zeekctl is needed: Zeek 9's logging framework rotates by itself when
##! Log::default_rotation_interval is set, and Log::rotation_format_func decides
##! where each rotated file goes.
##!
##! This file lives in scripts/live/ on purpose: maxguard/zeek/runner.py loads only
##! scripts/*.zeek, so reading a capture file never rotates anything.

module MaxGuardLive;

export {
    ## Where the interval folders are created. It must be on the same disk as
    ## Zeek's working folder: rotation renames files, and a rename cannot move
    ## a file to another disk.
    const archive_dir = "/data/zeek" &redef;
}

# One folder every 15 minutes. The sensor's compose file overrides this from the
# command line (Log::default_rotation_interval=1min for a quick test). Use a whole
# number of minutes that divides 60 (1, 5, 15, 30, 60 ...): Zeek rotates at
# multiples of the interval counted from midnight, and the folder names assume it.
redef Log::default_rotation_interval = 15 min;

# After a crash or a power cut the logs of the unfinished interval are left in
# the working folder. Rotate them into their interval folder at the next start.
redef LogAscii::enable_leftover_log_rotation = T;

## The start of the interval that contains time t, e.g. 14:22:10 -> 14:15:00.
function interval_start(t: time): time
    {
    local seconds = interval_to_double(Log::default_rotation_interval);
    return double_to_time(floor(time_to_double(t) / seconds) * seconds);
    }

## Called by Zeek once for every log file it rotates (conn, dns, http, ...).
function folder_per_interval(ri: Log::RotationFmtInfo): Log::RotationPath
    {
    local start = interval_start(ri$open);
    local dir = fmt("%s/%s", archive_dir, strftime("%Y-%m-%d-%H%M", start));
    local base = ri$path;  # "conn": Zeek adds ".log"

    # Zeek was restarted during this interval, so the folder already has a
    # conn.log from before the restart. Keep both: conn.141502.log is read as
    # conn.log too (maxguard/adapters/zeeklogs.py appends them).
    if ( file_size(fmt("%s/%s.log", dir, base)) >= 0 )
        base = fmt("%s.%s", ri$path, strftime("%H%M%S", ri$open));

    return Log::RotationPath($dir=dir, $file_basename=base);
    }

redef Log::rotation_format_func = folder_per_interval;
