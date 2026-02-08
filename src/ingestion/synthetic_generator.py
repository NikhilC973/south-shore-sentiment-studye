"""
Synthetic Data Generator — Realistic fallback data for development & testing.

Generates ~3500 posts mimicking real discourse patterns around the South Shore
ICE raid, with realistic temporal distribution, emotion profiles, and
neighborhood mentions that follow expected sentiment trajectories.

Updated: Extended to 7 phases through Dec 12, 2025 (building vacated).
Templates informed by Block Club Chicago verified reporting.
"""
import hashlib
import random
from datetime import datetime, timedelta, timezone
from typing import Generator

from src.utils.constants import (
    PHASES, SUBREDDITS, NEIGHBORHOOD_LEXICON, PLATFORMS,
)
from src.utils.logger import log


# ── Template Banks by Phase ──────────────────────────────────
# These templates simulate realistic discourse; NO real posts are reproduced.

TEMPLATES = {
    "pre": {
        "reddit": [
            "Has anyone heard about ICE activity near South Shore? Neighbors are getting nervous.",
            "Seeing more federal vehicles around 71st. Should we be concerned?",
            "Anyone know what's going on with immigration enforcement in the south side?",
            "Heads up South Shore - heard rumors about increased ICE presence this week.",
            "Just a normal day in South Shore, but there's definitely more tension in the air lately.",
            "Community meeting tonight about know-your-rights if ICE comes to your door.",
            "Can someone explain what rights tenants have if ICE shows up at their apartment building?",
            "Reminder: You do NOT have to open your door for ICE without a judicial warrant.",
            "South Shore mutual aid network just sent out a preparedness guide. DM me for link.",
            "Why does it feel like our neighborhood is being targeted? This is Chicago, not a border town.",
            "Worried about my neighbors. Some families are already afraid to send kids to school.",
            "Is there a legal aid hotline for immigrants in Chicago south side?",
        ],
        "news_comment": [
            "The mayor needs to address these federal overreach concerns before something happens.",
            "Chicago has always been a sanctuary city. We need to maintain that.",
            "People in South Shore deserve to feel safe in their own neighborhood.",
            "Immigration policy should not be enforced through military-style operations.",
            "I live near 71st and Jeffery. The tension is real and growing every day.",
        ],
    },
    "event": {
        "reddit": [
            "BREAKING: ICE raid happening RIGHT NOW in South Shore apartments. Helicopters overhead.",
            "Can hear flashbangs from my apartment on 71st. This is insane. Children live here.",
            "ICE agents in tactical gear going door to door in South Shore. Multiple buildings.",
            "They're breaking down doors in apartment buildings. People are terrified.",
            "This is a war zone. Flashbangs at 6am in a residential neighborhood with families.",
            "My building on Jeffery just got raided. Families crying in the hallway.",
            "Property damage to multiple apartment buildings. Who pays for this? Landlords? Tenants?",
            "911 calls going unanswered while this is happening. Our community is abandoned.",
            "Kids at the school on 71st can hear the flashbangs. Teachers trying to calm them down.",
            "Live updates: Multiple ICE vehicles, helicopters, and what appears to be CBP agents in South Shore.",
            "This is Operation Midway Blitz. Federal agents treating our neighborhood like a combat zone.",
            "Elderly residents trapped in their apartments because they're afraid to go outside.",
            "Where are our elected officials? Radio silence while our community is under siege.",
            "The trauma this is causing children in South Shore will last for years.",
            "Cell phone video of the raid is spreading. The whole neighborhood is in shock.",
            "Hundreds of agents in camo with rented moving trucks. They broke down doors at 7500 S South Shore.",
            "Neighbor says she was awoken by a black helicopter looping over the scene. Like a war zone.",
        ],
        "news_comment": [
            "Horrifying. Using flashbangs in residential buildings with children is unconscionable.",
            "This is not immigration enforcement. This is state violence against a community.",
            "My heart goes out to everyone in South Shore right now.",
            "When did enforcing immigration law require military tactics against families?",
            "The property damage alone shows this was excessive force.",
        ],
    },
    "post_week1": {
        "reddit": [
            "South Shore is traumatized. My neighbors haven't left their apartment since the raid.",
            "Organizing a community response meeting this Saturday at the church on 71st.",
            "Legal aid organizations are overwhelmed. If you're a lawyer, please volunteer.",
            "The anger in this community is justified. We were treated like criminals in our own homes.",
            "Community solidarity march planned for this weekend. South Shore stands together.",
            "NIJC has set up a hotline for affected families. Sharing the resource link.",
            "Children in South Shore are having nightmares about the helicopters and flashbangs.",
            "Mutual aid fund started for families affected by the raid. Link in comments.",
            "Local businesses on 71st reporting customers too afraid to come out. Economic impact is real.",
            "Anyone know a therapist who does trauma work and speaks Spanish? South Shore area.",
            "The DHS statement about 'Midway Blitz' is disgusting. They're bragging about terrorizing us.",
            "Property managers still haven't fixed the doors ICE broke. Tenants living with busted locks.",
            "Teachers at South Shore schools reporting behavioral changes in students since the raid.",
            "City council meeting tonight to discuss the aftermath. We need answers.",
            "Solidarity from Woodlawn. What happened in South Shore could happen anywhere.",
            "Residents returning to 7500 S South Shore Drive finding apartments ransacked. Zip ties and blood on floors.",
            "An army veteran living in the building had his door broken and belongings stolen during the raid.",
        ],
        "news_comment": [
            "The community response has been incredible. People coming together like I've never seen.",
            "Legal aid organizations need more funding to handle the aftermath of these raids.",
            "Mental health services for children affected by this should be the top priority.",
            "Property damage claims are piling up. Who holds ICE accountable?",
            "This story needs national attention. What happened in South Shore was wrong.",
        ],
    },
    "post_week2": {
        "reddit": [
            "Two weeks out from the raid and South Shore is finding its strength. Mutual aid is powerful.",
            "Counseling services now available at three locations in South Shore. Free, multilingual.",
            "The organizing that's come out of this tragedy is giving me hope.",
            "South Shore community associations filing formal complaints with DHS oversight.",
            "Fundraiser for affected families raised $50K in the first week. This community shows up.",
            "Know-your-rights workshops are now weekly. Attendance is growing.",
            "Long-term housing support needed for displaced families. Resources in thread.",
            "The trauma isn't over but the solidarity is real. South Shore is resilient.",
            "Media coverage is finally catching up to what we experienced on the ground.",
            "AP picked up the story. National spotlight on what happened here.",
            "Tenant organizing in South Shore buildings has quadrupled since the raid.",
            "Still processing what happened. The fear is subsiding but the anger remains.",
        ],
        "news_comment": [
            "South Shore's resilience in the face of this is truly inspiring.",
            "Long-term mental health support needs to be a priority for this community.",
            "The national coverage is important. Other communities need to prepare.",
            "Community organizations are doing the work the government should be doing.",
        ],
    },
    "post_weeks3_5": {
        "reddit": [
            "One month after the South Shore raid: what we've learned and what we're building.",
            "South Shore mutual aid network is now a permanent organization. Born from crisis.",
            "Block Club Chicago published the full distress call recordings. Heartbreaking but important.",
            "Policy proposals from South Shore community groups being presented to city council.",
            "Trauma-informed support groups continuing weekly. Healing takes time.",
            "South Side Weekly's investigation into the 911 audio is damning.",
            "Building a lasting infrastructure of care in South Shore. The raid changed everything.",
            "Reflections: the fear has transformed into organized power. That's South Shore.",
            "Legal cases moving forward. NIJC representing multiple affected families.",
            "Schools in South Shore implementing new support protocols for students.",
            "The building at 7500 S South Shore averaged more than one emergency call per day for 5 years before the raid.",
            "Judge just ordered the building cleared. Appointing a receiver to take control from the landlord.",
        ],
        "news_comment": [
            "The long-term organizing emerging from this crisis is exactly what communities need.",
            "South Shore is showing the country what resilience looks like.",
            "Policy changes are needed to prevent this from happening in other neighborhoods.",
        ],
    },
    "court_action": {
        "reddit": [
            "Tenants at 7500 S South Shore Drive just formed a union. About 30 residents demanding relocation help.",
            "The court-appointed receiver hasn't delivered on any promises. No heat, no security, sewage still flooding floors.",
            "Tenants union press conference today. Demanding $7,500 relocation assistance per family.",
            "The building owner is from Wisconsin. Bought three South Shore buildings in 2020, defaulted on all loans.",
            "Strength in Management — the property company — let conditions deteriorate before the raid. Guards removed, maintenance stopped.",
            "Court hearing update: Judge gave management more time to clean up but residents say nothing's changed.",
            "The foreclosure case has been going on for years. Wells Fargo wants the building. Tenants caught in the middle.",
            "Receiver Friedman also let feds use one of his other properties to stage immigration operations. Conflict of interest much?",
            "Where is the accountability for the landlord? Trinity Flood let this building become a death trap.",
            "Housing organizers from Southside Together helping residents navigate impossible choices.",
            "Only 37 occupants left in a 130-unit building. Most fled after the raid with nowhere to go.",
            "CHA needs to expedite Section 8 inspections for remaining residents with vouchers.",
        ],
        "news_comment": [
            "The tenants union is doing incredibly brave work in impossible circumstances.",
            "This is what happens when housing is treated as an investment vehicle instead of a human right.",
            "The judge needs to give these families more time. Finding housing in December is nearly impossible.",
            "Property management companies that let buildings deteriorate should face criminal charges.",
            "Block Club's reporting on this has been outstanding. Local journalism matters.",
        ],
    },
    "displacement": {
        "reddit": [
            "Judge denied the tenants union request for more time. Dec 12 deadline stands. Families scrambling.",
            "Workers installing steel window guards at 7500 S South Shore. They're sealing the building up.",
            "The judge said she doesn't care about political statements when the mayor wrote asking for more time.",
            "Being in a building with bad conditions is better than being homeless. That's the choice these families face.",
            "Tenants union accepting the $5,000 relocation offer. It's not enough but there's no other option.",
            "Today is the last day. Everyone has to be out of 7500 S South Shore Drive by end of day.",
            "From ICE raid to eviction in 73 days. This is what happened to South Shore residents.",
            "Where do 37 families go in December in Chicago? This is a housing crisis on top of a trauma crisis.",
            "The building is empty now. Boarded up. After everything those residents went through.",
            "Elevator couldn't even reach the top floor. Residents in wheelchairs couldn't get down safely.",
        ],
        "news_comment": [
            "The timeline from raid to eviction is devastating. These are real people with real lives.",
            "Finding a lease starting Dec 12 is impossible in Chicago. The judge should have known that.",
            "The $5,000 relocation assistance is a joke. Average security deposit plus first month is more than that.",
            "This story shows how enforcement actions create cascading displacement.",
        ],
    },
}

# ── Emotion Profiles by Phase ────────────────────────────────
# Expected emotional distribution (probabilities) per phase
EMOTION_PROFILES = {
    "pre": {"fear": 0.35, "anger": 0.15, "sadness": 0.10, "joy": 0.05,
            "surprise": 0.10, "disgust": 0.05, "gratitude": 0.10, "pride": 0.10},
    "event": {"fear": 0.40, "anger": 0.30, "sadness": 0.15, "joy": 0.01,
              "surprise": 0.08, "disgust": 0.04, "gratitude": 0.01, "pride": 0.01},
    "post_week1": {"fear": 0.15, "anger": 0.30, "sadness": 0.15, "joy": 0.05,
                   "surprise": 0.05, "disgust": 0.05, "gratitude": 0.15, "pride": 0.10},
    "post_week2": {"fear": 0.08, "anger": 0.15, "sadness": 0.10, "joy": 0.15,
                   "surprise": 0.05, "disgust": 0.02, "gratitude": 0.25, "pride": 0.20},
    "post_weeks3_5": {"fear": 0.05, "anger": 0.10, "sadness": 0.08, "joy": 0.15,
                      "surprise": 0.05, "disgust": 0.02, "gratitude": 0.25, "pride": 0.30},
    "court_action": {"fear": 0.10, "anger": 0.25, "sadness": 0.20, "joy": 0.03,
                     "surprise": 0.05, "disgust": 0.07, "gratitude": 0.15, "pride": 0.15},
    "displacement": {"fear": 0.15, "anger": 0.30, "sadness": 0.30, "joy": 0.02,
                     "surprise": 0.03, "disgust": 0.08, "gratitude": 0.07, "pride": 0.05},
}

# ── Temporal Distribution ────────────────────────────────────
PHASE_POST_WEIGHTS = {
    "pre": 0.12,            # Moderate baseline chatter
    "event": 0.22,          # Spike during raid
    "post_week1": 0.20,     # High aftermath volume
    "post_week2": 0.14,     # Declining but significant
    "post_weeks3_5": 0.12,  # Extended tail
    "court_action": 0.12,   # Renewed attention with court
    "displacement": 0.08,   # Final phase — smaller but intense
}

SUBREDDIT_WEIGHTS = {
    "Chicago": 0.30, "news": 0.15, "Illinois": 0.10, "politics": 0.10,
    "AskChicago": 0.08, "EyesOnIce": 0.07, "moderatepolitics": 0.05,
    "WindyCity": 0.05, "ICE_Raids": 0.04, "AskConservatives": 0.03,
    "somethingiswrong2024": 0.02, "50501Chicago": 0.01,
}


def _random_datetime_in_phase(phase: str, rng: random.Random) -> datetime:
    """Generate a random datetime within a phase window."""
    phase_info = PHASES[phase]
    start = datetime.strptime(phase_info["start"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end = datetime.strptime(phase_info["end"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    delta = end - start
    random_offset = timedelta(seconds=rng.randint(0, int(delta.total_seconds())))
    return start + random_offset


def _add_neighborhood_mentions(text: str, rng: random.Random) -> tuple[str, list[str]]:
    """Potentially insert neighborhood references and return detected neighborhoods."""
    detected = []
    for neighborhood, terms in NEIGHBORHOOD_LEXICON.items():
        for term in terms:
            if term.lower() in text.lower():
                detected.append(neighborhood)
                break

    # If no neighborhood mentioned, sometimes add one
    if not detected and rng.random() < 0.4:
        neighborhood = rng.choice(list(NEIGHBORHOOD_LEXICON.keys()))
        terms = NEIGHBORHOOD_LEXICON[neighborhood]
        mention = rng.choice(terms)
        detected.append(neighborhood)
        # Don't modify the text; just tag it

    return text, list(set(detected))


def generate_synthetic_data(
    n_posts: int = 3500,
    seed: int = 42,
) -> list[dict]:
    """
    Generate realistic synthetic posts following expected temporal and
    emotional distributions.

    Returns list of dicts matching posts_raw schema.
    """
    rng = random.Random(seed)
    posts = []

    # Determine posts per phase
    phase_counts = {}
    remaining = n_posts
    phases = list(PHASE_POST_WEIGHTS.keys())
    for i, phase in enumerate(phases):
        if i == len(phases) - 1:
            phase_counts[phase] = remaining
        else:
            count = int(n_posts * PHASE_POST_WEIGHTS[phase])
            phase_counts[phase] = count
            remaining -= count

    # Subreddit selection weights
    sub_names = list(SUBREDDIT_WEIGHTS.keys())
    sub_weights = list(SUBREDDIT_WEIGHTS.values())

    for phase, count in phase_counts.items():
        templates_reddit = TEMPLATES[phase]["reddit"]
        templates_news = TEMPLATES[phase]["news_comment"]

        for i in range(count):
            # Platform split: 75% reddit, 25% news
            platform = rng.choices(
                ["reddit", "news_comment"],
                weights=[0.75, 0.25],
            )[0]

            if platform == "reddit":
                text = rng.choice(templates_reddit)
                # Add some variation
                variations = [
                    lambda t: t,
                    lambda t: t + " " + rng.choice(["smh", "unreal", "this is insane", "stay safe everyone", "prayers up"]),
                    lambda t: "Just saw this: " + t.lower(),
                    lambda t: t + " What are we supposed to do?",
                    lambda t: "Can confirm. " + t,
                    lambda t: f"Thread: {t}",
                ]
                text = rng.choice(variations)(text)

                source = rng.choices(sub_names, weights=sub_weights)[0]
                post_type = rng.choice(["submission", "comment", "comment", "comment"])  # 75% comments
            else:
                text = rng.choice(templates_news)
                source = rng.choice(["Block Club Chicago", "WBEZ", "Chicago Sun-Times",
                                      "South Side Weekly", "AP News"])
                post_type = rng.choice(["article", "comment", "comment", "comment"])

            dt = _random_datetime_in_phase(phase, rng)
            text, neighborhoods = _add_neighborhood_mentions(text, rng)

            post_id = hashlib.md5(f"{phase}_{i}_{text[:30]}_{dt.isoformat()}".encode()).hexdigest()[:16]

            posts.append({
                "id": f"syn_{post_id}",
                "platform": platform,
                "source": source,
                "url": f"https://synthetic.example.com/{post_id}",
                "dt_utc": dt.isoformat(),
                "text": text,
                "title": text[:60] + "..." if post_type in ("submission", "article") else None,
                "author_display": f"user_{rng.randint(1000, 9999)}",
                "score": rng.randint(-5, 500) if platform == "reddit" else 0,
                "like_count": rng.randint(0, 200),
                "reply_count": rng.randint(0, 50),
                "share_count": rng.randint(0, 20),
                "parent_id": f"syn_parent_{rng.randint(1, 1000)}" if post_type == "comment" else None,
                "post_type": post_type,
                "detected_locs": neighborhoods,
                "anchors": phase,
                "search_term": rng.choice([
                    "South Shore ICE", "Chicago ICE raid", "Operation Midway Blitz",
                    "South Shore raid", "ICE raid Chicago apartment",
                    "South Shore tenants union", "7500 South Shore Drive",
                ]),
            })

    rng.shuffle(posts)
    log.info(f"Generated {len(posts)} synthetic posts across {len(PHASES)} phases")

    # Log distribution
    from collections import Counter
    phase_dist = Counter(p["anchors"] for p in posts)
    platform_dist = Counter(p["platform"] for p in posts)
    log.info(f"Phase distribution: {dict(phase_dist)}")
    log.info(f"Platform distribution: {dict(platform_dist)}")

    return posts


if __name__ == "__main__":
    import json
    posts = generate_synthetic_data(n_posts=3500)
    print(f"Generated {len(posts)} posts")
    print(json.dumps(posts[0], indent=2, default=str))
