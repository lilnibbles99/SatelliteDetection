from satellite_tle import fetch_tle_from_celestrak

norad_id_iss = 25544 # ISS (ZARYA)
print(fetch_tle_from_celestrak(norad_id_iss))

from satellite_tle import fetch_all_tles, fetch_latest_tles

norad_ids = [25544, # ISS (ZARYA)
             42983, # QIKCOM-1
             40379] # GRIFEX

# Uses default sources and compares TLE set from each source and
# returns the latest one for each satellite
tles = fetch_latest_tles(norad_ids)

for norad_id, (source, tle) in tles.items():
    print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))

# Uses default sources and returns the TLE sets from all source for
# each satellite
tles = fetch_all_tles(norad_ids)

for norad_id, tle_list in tles.items():
    for source, tle in tle_list:
        print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))

# Defines custom sources
sources = [
    ('CalPoly','http://mstl.atl.calpoly.edu/~ops/keps/kepler.txt'),
    ('Celestrak (active)','https://celestrak.org/NORAD/elements/active.txt')
]

# Uses custom sources (fetch_all_tles can also be used with the same
# parameters)
tles = fetch_latest_tles(norad_ids, sources=sources)

for norad_id, (source, tle) in tles.items():
    print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))

spacetrack_config= {
    'identity': 'my_username',
    'password': 'my_secret_password'
}

# Uses default sources and Space-Track.org (fetch_all_tles can also
# be used with the same parameters)
tles = fetch_latest_tles(norad_ids, spacetrack_config=spacetrack_config)

for norad_id, (source, tle) in tles.items():
    print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))

# Uses only Space-Track.org (fetch_all_tles can also be used with the
# same parameters)
tles = fetch_latest_tles(norad_ids, sources=[], spacetrack_config=spacetrack_config)

for norad_id, (source, tle) in tles.items():
    print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))

# Uses custom sources and Space-Track.org (fetch_all_tles can also be
# used with the same parameters)
tles = fetch_latest_tles(norad_ids, sources=sources, spacetrack_config=spacetrack_config)

for norad_id, (source, tle) in tles.items():
    print('{:5d} {:23s}: {:23s}'.format(norad_id, tle[0], source))