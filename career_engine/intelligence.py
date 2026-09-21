"""Read-only career intelligence facade."""
from .outcomes import learning_signals

def build_career_intelligence(store):
    return learning_signals(
        store.collection("applications",[]),
        store.collection("opportunities",[]),
        store.collection("interviews",[]),
        store.collection("skill_gaps",[]),
    )
