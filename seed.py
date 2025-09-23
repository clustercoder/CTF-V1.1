# seed.py — cleaned seeder
from app import db, Challenge, hash_flag, app

with app.app_context():
    db.create_all()

    challenges = [
        Challenge(
            id="mosaicpixels",
            title="Mosaic Pixels",
            description='''
You've intercepted a classified transmission from a secret cyber lab. Buried inside is a digital message containing a highly sensitive secret. But the lab's AI security has scrambled the signal: the message has been fragmented into hundreds of pieces and camouflaged with the lab's signature emblem.
Some fragments overlap, some hide beneath the emblem, and others appear incomplete. To make sense of the transmission, you'll need to observe patterns across the pieces and identify how the signal emerges when the fragments interact.
Careful observation will reveal that the darkest marks carry the truth, while distractions in the background may mislead. Only by leveraging the collective behavior of the pieces will the hidden information become readable.
This isn't just a puzzle it's a test of precision, patience, and ingenuity. One misstep, one overlooked fragment, and the secret could remain hidden indefinitely. https://drive.google.com/drive/folders/1WoSBU00z35MbBBJJIigpkfDy-rCFCIt_?usp=sharing
''',
            flag_hash=hash_flag("GDG{Fr46M3N73D_P1X315_r3UN173D_6D6_25}"),
            points=600,
        ),
        Challenge(
            id="webbit",
            title="Webbit 🍪",
            description="That escalated quickly  10.125.160.46:4000",
            flag_hash=hash_flag("GDG{c00k13_m0nst3r_l1k3s_c00k13s}"),
            points=600,
        ),
        Challenge(
            id="twink",
            title="classmate registers",
            description='''A mysterious file was discovered on a suspect's computer. Something hidden lies within. Can you uncover the secret it’s hiding?
 https://drive.google.com/file/d/1nBjXair7TNFDkL5CZY2Hzn83lbdA-btr/view?usp=sharing
 Flag Format GDG{...}''',
            flag_hash=hash_flag("GDG{WinRegistReddingFlag}"),
            points=600,
        ),
        Challenge(
            id="envrn",
            title="6EQUJ5",
            description="search your env",
            flag_hash=hash_flag("GDG{codewithjoy}"),
            points=606,
        ),
        Challenge(
            id="mob",
            title="MAD",
            description="A suspicious Android APK was found on a compromised device. The app claims to be a simple calculator, but it seems to do more than just math. Can you uncover its hidden functionality and extract the secret flag? https://drive.google.com/file/d/1lrfT64hVLNlaQmgzgKGAFRwv-aB5zvfo/view?usp=sharing",
            flag_hash=hash_flag("GDG{c@1cU15}"),
            points=600,
        ) 
    ]

    for chall in challenges:
        existing = Challenge.query.get(chall.id)
        if existing:
            existing.title = chall.title
            existing.description = chall.description
            existing.flag_hash = chall.flag_hash
            existing.points = chall.points
            existing.docker_image = chall.docker_image
            existing.port = chall.port
        else:
            db.session.add(chall)

    db.session.commit()
    print("✅ Challenges seeded/updated successfully.")
