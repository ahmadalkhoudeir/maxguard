"""Decoys: fake services on their own IP address (Fiona, FIO-06).

A decoy only answers connections made to it and writes one line per connection
to decoy.log. Rule decoy.contact (maxguard/rules/decoy.py) turns those lines
into critical findings. Decoys are not sensors (CLAUDE.md rule 5).
"""
