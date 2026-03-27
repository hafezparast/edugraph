#!/usr/bin/env python3
"""
Generate CEFR-based language knowledge graphs for all 13 languages.

Usage:
    python generate_languages.py           # generate all
    python generate_languages.py en de     # generate specific languages
"""

import json
import sys
import os
import copy
from collections import defaultdict, deque

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "data")

# ============================================================
# CEFR LEVELS (Books)
# ============================================================
BOOKS = [
    {"id": "book.a1_1", "name": "A1.1 Breakthrough Lower", "color": "#ef4444", "order": 1},
    {"id": "book.a1_2", "name": "A1.2 Breakthrough Upper", "color": "#f97316", "order": 2},
    {"id": "book.a2_1", "name": "A2.1 Waystage Lower", "color": "#f59e0b", "order": 3},
    {"id": "book.a2_2", "name": "A2.2 Waystage Upper", "color": "#eab308", "order": 4},
    {"id": "book.b1_1", "name": "B1.1 Threshold Lower", "color": "#84cc16", "order": 5},
    {"id": "book.b1_2", "name": "B1.2 Threshold Upper", "color": "#22c55e", "order": 6},
    {"id": "book.b2_1", "name": "B2.1 Vantage Lower", "color": "#14b8a6", "order": 7},
    {"id": "book.b2_2", "name": "B2.2 Vantage Upper", "color": "#06b6d4", "order": 8},
    {"id": "book.c1_1", "name": "C1.1 Effective Lower", "color": "#3b82f6", "order": 9},
    {"id": "book.c1_2", "name": "C1.2 Effective Upper", "color": "#6366f1", "order": 10},
    {"id": "book.c2_1", "name": "C2.1 Mastery Lower", "color": "#8b5cf6", "order": 11},
    {"id": "book.c2_2", "name": "C2.2 Mastery Upper", "color": "#a855f7", "order": 12},
]

BOOK_MAP = {b["id"]: b for b in BOOKS}

# ============================================================
# TEMPLATE NODES (level, type_prefix, slug, label, tags)
# ============================================================
TEMPLATE_NODES = [
    # A1.1
    ("a1_1", "k", "alphabet_phonics", "Alphabet and Phonics", ["phonology"]),
    ("a1_1", "k", "greetings_farewells", "Greetings and Farewells", ["vocabulary", "interaction"]),
    ("a1_1", "k", "personal_pronouns", "Personal Pronouns", ["grammar"]),
    ("a1_1", "k", "present_simple_be", "Present Tense: 'to be'", ["grammar", "verbs"]),
    ("a1_1", "k", "numbers_1_20", "Numbers 1-20", ["vocabulary"]),
    ("a1_1", "k", "basic_nouns", "Basic Concrete Nouns", ["vocabulary"]),
    ("a1_1", "s", "introduce_self", "Can introduce self", ["speaking", "interaction"]),
    ("a1_1", "s", "understand_simple_instructions", "Can understand simple instructions", ["listening"]),
    ("a1_1", "s", "ask_yes_no", "Can ask/answer yes-no questions", ["speaking"]),
    ("a1_1", "s", "copy_words", "Can copy familiar words", ["writing"]),
    # A1.2
    ("a1_2", "k", "present_simple_regular", "Present Simple: Regular Verbs", ["grammar", "verbs"]),
    ("a1_2", "k", "articles_demonstratives", "Articles and Demonstratives", ["grammar"]),
    ("a1_2", "k", "basic_adjectives", "Basic Adjectives", ["vocabulary", "grammar"]),
    ("a1_2", "k", "prepositions_place", "Prepositions of Place", ["grammar"]),
    ("a1_2", "k", "numbers_dates_time", "Numbers, Dates and Time", ["vocabulary"]),
    ("a1_2", "k", "food_drink_vocab", "Food, Drink and Shopping", ["vocabulary"]),
    ("a1_2", "s", "describe_objects_people", "Can describe objects and people", ["speaking"]),
    ("a1_2", "s", "ask_where_when", "Can ask where/when questions", ["speaking"]),
    ("a1_2", "s", "order_food", "Can order food and drink", ["interaction"]),
    ("a1_2", "s", "fill_simple_form", "Can fill in a simple form", ["writing"]),
    # A2.1
    ("a2_1", "k", "past_simple", "Past Simple", ["grammar", "verbs"]),
    ("a2_1", "k", "possessives", "Possessives", ["grammar"]),
    ("a2_1", "k", "adverbs_frequency", "Adverbs of Frequency", ["grammar"]),
    ("a2_1", "k", "conjunctions_basic", "Basic Conjunctions", ["grammar"]),
    ("a2_1", "k", "daily_routine_vocab", "Daily Routine Vocabulary", ["vocabulary"]),
    ("a2_1", "k", "countable_uncountable", "Countable and Uncountable Nouns", ["grammar"]),
    ("a2_1", "s", "narrate_past_events", "Can narrate past events simply", ["speaking"]),
    ("a2_1", "s", "make_suggestions", "Can make suggestions", ["interaction"]),
    ("a2_1", "s", "write_short_message", "Can write a short message", ["writing"]),
    ("a2_1", "s", "understand_short_text", "Can understand short texts", ["reading"]),
    # A2.2
    ("a2_2", "k", "future_forms", "Future Forms", ["grammar", "verbs"]),
    ("a2_2", "k", "comparatives_superlatives", "Comparatives and Superlatives", ["grammar"]),
    ("a2_2", "k", "modal_verbs_basic", "Basic Modal Verbs", ["grammar", "verbs"]),
    ("a2_2", "k", "object_pronouns", "Object Pronouns and Reflexives", ["grammar"]),
    ("a2_2", "k", "travel_directions_vocab", "Travel and Directions Vocabulary", ["vocabulary"]),
    ("a2_2", "k", "imperative_mood", "Imperative Mood", ["grammar"]),
    ("a2_2", "s", "give_directions", "Can give and follow directions", ["speaking"]),
    ("a2_2", "s", "make_plans", "Can make future plans", ["speaking"]),
    ("a2_2", "s", "write_personal_letter", "Can write a personal letter", ["writing"]),
    ("a2_2", "s", "describe_experiences", "Can describe experiences", ["speaking"]),
    # B1.1
    ("b1_1", "k", "present_perfect", "Present Perfect", ["grammar", "verbs"]),
    ("b1_1", "k", "relative_clauses", "Relative Clauses (Defining)", ["grammar"]),
    ("b1_1", "k", "first_conditional", "First Conditional", ["grammar"]),
    ("b1_1", "k", "passive_voice", "Passive Voice (Present/Past)", ["grammar"]),
    ("b1_1", "k", "phrasal_verbs", "Common Phrasal Verbs", ["vocabulary"]),
    ("b1_1", "k", "connectors_discourse", "Discourse Connectors", ["grammar"]),
    ("b1_1", "s", "express_opinions", "Can express and justify opinions", ["speaking"]),
    ("b1_1", "s", "understand_main_points", "Can understand main points of speech", ["listening"]),
    ("b1_1", "s", "write_structured_paragraph", "Can write structured paragraphs", ["writing"]),
    ("b1_1", "s", "handle_travel_situations", "Can handle most travel situations", ["interaction"]),
    # B1.2
    ("b1_2", "k", "past_perfect", "Past Perfect", ["grammar", "verbs"]),
    ("b1_2", "k", "second_conditional", "Second Conditional", ["grammar"]),
    ("b1_2", "k", "reported_speech_basic", "Reported Speech (Basic)", ["grammar"]),
    ("b1_2", "k", "gerunds_infinitives", "Gerunds and Infinitives", ["grammar"]),
    ("b1_2", "k", "quantifiers", "Quantifiers and Determiners", ["grammar"]),
    ("b1_2", "k", "work_education_vocab", "Work and Education Vocabulary", ["vocabulary"]),
    ("b1_2", "s", "tell_story_detail", "Can tell a story in detail", ["speaking"]),
    ("b1_2", "s", "write_formal_email", "Can write a formal email", ["writing"]),
    ("b1_2", "s", "summarize_text", "Can summarize a text", ["reading", "speaking"]),
    ("b1_2", "s", "participate_discussion", "Can participate in discussions", ["interaction"]),
    # B2.1
    ("b2_1", "k", "third_conditional", "Third Conditional", ["grammar"]),
    ("b2_1", "k", "passive_advanced", "Advanced Passive Constructions", ["grammar"]),
    ("b2_1", "k", "modal_perfects", "Modal Perfects", ["grammar", "verbs"]),
    ("b2_1", "k", "cleft_sentences", "Cleft and Emphasis Structures", ["grammar"]),
    ("b2_1", "k", "collocations_idioms", "Collocations and Idioms", ["vocabulary"]),
    ("b2_1", "k", "abstract_vocab", "Abstract and Academic Vocabulary", ["vocabulary"]),
    ("b2_1", "s", "present_argument", "Can present a clear argument", ["speaking"]),
    ("b2_1", "s", "understand_extended_speech", "Can understand extended speech", ["listening"]),
    ("b2_1", "s", "write_essay", "Can write a clear essay", ["writing"]),
    ("b2_1", "s", "negotiate", "Can negotiate and compromise", ["interaction"]),
    # B2.2
    ("b2_2", "k", "mixed_conditionals", "Mixed Conditionals", ["grammar"]),
    ("b2_2", "k", "subjunctive_mood", "Subjunctive and Formal Structures", ["grammar"]),
    ("b2_2", "k", "inversion", "Inversion for Emphasis", ["grammar"]),
    ("b2_2", "k", "reported_speech_advanced", "Advanced Reported Speech", ["grammar"]),
    ("b2_2", "k", "register_formality", "Register and Formality", ["pragmatics"]),
    ("b2_2", "k", "word_formation", "Word Formation (Affixes)", ["vocabulary"]),
    ("b2_2", "s", "discuss_complex_topics", "Can discuss complex topics fluently", ["speaking"]),
    ("b2_2", "s", "write_report", "Can write a detailed report", ["writing"]),
    ("b2_2", "s", "read_authentic_texts", "Can read authentic texts with ease", ["reading"]),
    ("b2_2", "s", "mediate_conversation", "Can mediate in a conversation", ["interaction"]),
    # C1.1
    ("c1_1", "k", "advanced_tense_aspect", "Advanced Tense and Aspect", ["grammar"]),
    ("c1_1", "k", "discourse_pragmatics", "Discourse and Pragmatics", ["pragmatics"]),
    ("c1_1", "k", "ellipsis_substitution", "Ellipsis and Substitution", ["grammar"]),
    ("c1_1", "k", "advanced_relative_clauses", "Advanced Relative/Noun Clauses", ["grammar"]),
    ("c1_1", "k", "specialized_vocab", "Specialized Domain Vocabulary", ["vocabulary"]),
    ("c1_1", "k", "figurative_language", "Figurative Language", ["vocabulary", "pragmatics"]),
    ("c1_1", "s", "present_complex_ideas", "Can present complex ideas precisely", ["speaking"]),
    ("c1_1", "s", "write_academic_text", "Can write academic text", ["writing"]),
    ("c1_1", "s", "understand_implicit", "Can understand implicit meanings", ["listening", "reading"]),
    ("c1_1", "s", "professional_discourse", "Can engage in professional discourse", ["interaction"]),
    # C1.2
    ("c1_2", "k", "stylistic_variation", "Stylistic Variation", ["pragmatics"]),
    ("c1_2", "k", "advanced_cohesion", "Advanced Cohesion Devices", ["grammar"]),
    ("c1_2", "k", "sociolinguistic_awareness", "Sociolinguistic Awareness", ["pragmatics"]),
    ("c1_2", "k", "etymology_word_roots", "Etymology and Word Roots", ["vocabulary"]),
    ("c1_2", "k", "complex_sentence_patterns", "Complex Sentence Patterns", ["grammar"]),
    ("c1_2", "s", "write_persuasive_text", "Can write persuasive text", ["writing"]),
    ("c1_2", "s", "follow_complex_interaction", "Can follow complex interaction", ["listening"]),
    ("c1_2", "s", "reformulate_ideas", "Can reformulate ideas flexibly", ["speaking"]),
    ("c1_2", "s", "critique_text", "Can critically evaluate texts", ["reading"]),
    ("c1_2", "s", "deliver_spontaneous_speech", "Can deliver spontaneous speech", ["speaking"]),
    # C2.1
    ("c2_1", "k", "near_native_grammar", "Near-native Grammatical Precision", ["grammar"]),
    ("c2_1", "k", "pragmatic_competence", "Pragmatic Competence", ["pragmatics"]),
    ("c2_1", "k", "literary_analysis", "Literary and Textual Analysis", ["pragmatics"]),
    ("c2_1", "k", "technical_writing", "Technical Writing Conventions", ["writing"]),
    ("c2_1", "k", "humor_wordplay", "Humor, Wordplay, Cultural Nuance", ["vocabulary", "pragmatics"]),
    ("c2_1", "s", "write_publishable", "Can produce publication-quality text", ["writing"]),
    ("c2_1", "s", "interpret_subtlety", "Can interpret all subtleties", ["reading", "listening"]),
    ("c2_1", "s", "simultaneous_mediation", "Can mediate complex situations", ["interaction"]),
    ("c2_1", "s", "adapt_any_audience", "Can adapt to any audience", ["speaking"]),
    ("c2_1", "s", "extended_monologue", "Can sustain extended monologue", ["speaking"]),
    # C2.2
    ("c2_2", "k", "language_as_system", "Language as a System", ["metalinguistic"]),
    ("c2_2", "k", "historical_change", "Historical Language Change", ["metalinguistic"]),
    ("c2_2", "k", "creative_mastery", "Creative Language Mastery", ["writing", "pragmatics"]),
    ("c2_2", "k", "professional_specialization", "Professional Specialization", ["vocabulary"]),
    ("c2_2", "s", "native_fluency", "Native-equivalent fluency", ["speaking"]),
    ("c2_2", "s", "write_any_genre", "Can write in any genre", ["writing"]),
    ("c2_2", "s", "teach_language", "Can teach the language", ["metalinguistic"]),
    ("c2_2", "s", "translate_interpret", "Can translate/interpret professionally", ["interaction"]),
]

# ============================================================
# TEMPLATE EDGES (source_slug, target_slug)
# Slugs are "level.type.name" without lang prefix
# ============================================================
TEMPLATE_EDGES = [
    # Within A1.1
    ("a1_1.k.greetings_farewells", "a1_1.s.introduce_self"),
    ("a1_1.k.personal_pronouns", "a1_1.s.introduce_self"),
    ("a1_1.k.present_simple_be", "a1_1.s.ask_yes_no"),
    ("a1_1.k.basic_nouns", "a1_1.s.understand_simple_instructions"),
    ("a1_1.k.alphabet_phonics", "a1_1.s.copy_words"),
    ("a1_1.k.numbers_1_20", "a1_1.s.understand_simple_instructions"),
    # Within A1.2
    ("a1_2.k.present_simple_regular", "a1_2.s.describe_objects_people"),
    ("a1_2.k.basic_adjectives", "a1_2.s.describe_objects_people"),
    ("a1_2.k.prepositions_place", "a1_2.s.ask_where_when"),
    ("a1_2.k.food_drink_vocab", "a1_2.s.order_food"),
    ("a1_2.k.numbers_dates_time", "a1_2.s.fill_simple_form"),
    ("a1_2.k.articles_demonstratives", "a1_2.s.describe_objects_people"),
    # Within A2.1
    ("a2_1.k.past_simple", "a2_1.s.narrate_past_events"),
    ("a2_1.k.daily_routine_vocab", "a2_1.s.narrate_past_events"),
    ("a2_1.k.conjunctions_basic", "a2_1.s.write_short_message"),
    ("a2_1.k.countable_uncountable", "a2_1.s.understand_short_text"),
    ("a2_1.k.possessives", "a2_1.s.write_short_message"),
    ("a2_1.k.adverbs_frequency", "a2_1.s.make_suggestions"),
    # Within A2.2
    ("a2_2.k.future_forms", "a2_2.s.make_plans"),
    ("a2_2.k.comparatives_superlatives", "a2_2.s.describe_experiences"),
    ("a2_2.k.travel_directions_vocab", "a2_2.s.give_directions"),
    ("a2_2.k.imperative_mood", "a2_2.s.give_directions"),
    ("a2_2.k.modal_verbs_basic", "a2_2.s.make_plans"),
    ("a2_2.k.object_pronouns", "a2_2.s.write_personal_letter"),
    # Within B1.1
    ("b1_1.k.present_perfect", "b1_1.s.express_opinions"),
    ("b1_1.k.connectors_discourse", "b1_1.s.write_structured_paragraph"),
    ("b1_1.k.passive_voice", "b1_1.s.understand_main_points"),
    ("b1_1.k.first_conditional", "b1_1.s.handle_travel_situations"),
    ("b1_1.k.phrasal_verbs", "b1_1.s.understand_main_points"),
    ("b1_1.k.relative_clauses", "b1_1.s.write_structured_paragraph"),
    # Within B1.2
    ("b1_2.k.past_perfect", "b1_2.s.tell_story_detail"),
    ("b1_2.k.reported_speech_basic", "b1_2.s.summarize_text"),
    ("b1_2.k.gerunds_infinitives", "b1_2.s.write_formal_email"),
    ("b1_2.k.work_education_vocab", "b1_2.s.participate_discussion"),
    ("b1_2.k.quantifiers", "b1_2.s.participate_discussion"),
    # Within B2.1
    ("b2_1.k.third_conditional", "b2_1.s.present_argument"),
    ("b2_1.k.modal_perfects", "b2_1.s.present_argument"),
    ("b2_1.k.collocations_idioms", "b2_1.s.negotiate"),
    ("b2_1.k.abstract_vocab", "b2_1.s.write_essay"),
    ("b2_1.k.cleft_sentences", "b2_1.s.understand_extended_speech"),
    ("b2_1.k.passive_advanced", "b2_1.s.write_essay"),
    # Within B2.2
    ("b2_2.k.mixed_conditionals", "b2_2.s.discuss_complex_topics"),
    ("b2_2.k.register_formality", "b2_2.s.write_report"),
    ("b2_2.k.word_formation", "b2_2.s.read_authentic_texts"),
    ("b2_2.k.inversion", "b2_2.s.discuss_complex_topics"),
    ("b2_2.k.subjunctive_mood", "b2_2.s.discuss_complex_topics"),
    ("b2_2.k.reported_speech_advanced", "b2_2.s.mediate_conversation"),
    # Within C1.1
    ("c1_1.k.discourse_pragmatics", "c1_1.s.professional_discourse"),
    ("c1_1.k.figurative_language", "c1_1.s.understand_implicit"),
    ("c1_1.k.specialized_vocab", "c1_1.s.write_academic_text"),
    ("c1_1.k.advanced_tense_aspect", "c1_1.s.present_complex_ideas"),
    ("c1_1.k.ellipsis_substitution", "c1_1.s.professional_discourse"),
    ("c1_1.k.advanced_relative_clauses", "c1_1.s.write_academic_text"),
    # Within C1.2
    ("c1_2.k.stylistic_variation", "c1_2.s.write_persuasive_text"),
    ("c1_2.k.advanced_cohesion", "c1_2.s.write_persuasive_text"),
    ("c1_2.k.sociolinguistic_awareness", "c1_2.s.follow_complex_interaction"),
    ("c1_2.k.etymology_word_roots", "c1_2.s.critique_text"),
    ("c1_2.k.complex_sentence_patterns", "c1_2.s.deliver_spontaneous_speech"),
    # Within C2.1
    ("c2_1.k.pragmatic_competence", "c2_1.s.adapt_any_audience"),
    ("c2_1.k.literary_analysis", "c2_1.s.interpret_subtlety"),
    ("c2_1.k.humor_wordplay", "c2_1.s.interpret_subtlety"),
    ("c2_1.k.technical_writing", "c2_1.s.write_publishable"),
    ("c2_1.k.near_native_grammar", "c2_1.s.extended_monologue"),
    # Within C2.2
    ("c2_2.k.creative_mastery", "c2_2.s.write_any_genre"),
    ("c2_2.k.language_as_system", "c2_2.s.teach_language"),
    ("c2_2.k.historical_change", "c2_2.s.teach_language"),
    ("c2_2.k.professional_specialization", "c2_2.s.native_fluency"),
    # Cross-level Knowledge chains
    ("a1_1.k.present_simple_be", "a1_2.k.present_simple_regular"),
    ("a1_1.k.numbers_1_20", "a1_2.k.numbers_dates_time"),
    ("a1_1.k.basic_nouns", "a1_2.k.articles_demonstratives"),
    ("a1_1.k.basic_nouns", "a2_1.k.countable_uncountable"),
    ("a1_1.k.personal_pronouns", "a2_1.k.possessives"),
    ("a1_1.k.personal_pronouns", "a2_2.k.object_pronouns"),
    ("a1_2.k.present_simple_regular", "a2_1.k.past_simple"),
    ("a1_2.k.present_simple_regular", "a2_1.k.adverbs_frequency"),
    ("a1_2.k.basic_adjectives", "a2_2.k.comparatives_superlatives"),
    ("a1_2.k.prepositions_place", "a2_2.k.travel_directions_vocab"),
    ("a2_1.k.past_simple", "a2_2.k.future_forms"),
    ("a2_1.k.conjunctions_basic", "b1_1.k.connectors_discourse"),
    ("a2_2.k.modal_verbs_basic", "b2_1.k.modal_perfects"),
    ("a2_2.k.future_forms", "b1_1.k.first_conditional"),
    ("a2_1.k.past_simple", "b1_1.k.present_perfect"),
    ("b1_1.k.present_perfect", "b1_2.k.past_perfect"),
    ("b1_1.k.first_conditional", "b1_2.k.second_conditional"),
    ("b1_1.k.passive_voice", "b2_1.k.passive_advanced"),
    ("b1_1.k.relative_clauses", "c1_1.k.advanced_relative_clauses"),
    ("b1_2.k.second_conditional", "b2_1.k.third_conditional"),
    ("b1_2.k.reported_speech_basic", "b2_2.k.reported_speech_advanced"),
    ("b2_1.k.third_conditional", "b2_2.k.mixed_conditionals"),
    ("b2_1.k.collocations_idioms", "c2_1.k.humor_wordplay"),
    ("b2_1.k.abstract_vocab", "c1_1.k.specialized_vocab"),
    ("b2_2.k.register_formality", "c1_1.k.discourse_pragmatics"),
    ("b2_2.k.word_formation", "c1_2.k.etymology_word_roots"),
    ("b2_2.k.subjunctive_mood", "c1_1.k.advanced_tense_aspect"),
    ("b2_2.k.inversion", "c1_2.k.complex_sentence_patterns"),
    ("c1_1.k.figurative_language", "c2_1.k.literary_analysis"),
    ("c1_1.k.discourse_pragmatics", "c2_1.k.pragmatic_competence"),
    ("c1_2.k.sociolinguistic_awareness", "c2_2.k.historical_change"),
    ("c1_2.k.stylistic_variation", "c2_2.k.creative_mastery"),
    ("c2_1.k.technical_writing", "c2_2.k.professional_specialization"),
    ("c2_1.k.near_native_grammar", "c2_2.k.language_as_system"),
    # Cross-level Skill chains
    ("a1_1.s.copy_words", "a1_2.s.fill_simple_form"),
    ("a1_1.s.introduce_self", "a1_2.s.describe_objects_people"),
    ("a1_2.s.describe_objects_people", "a2_2.s.describe_experiences"),
    ("a1_2.s.order_food", "a2_1.s.make_suggestions"),
    ("a2_1.s.write_short_message", "a2_2.s.write_personal_letter"),
    ("a2_1.s.understand_short_text", "b1_1.s.understand_main_points"),
    ("a2_2.s.write_personal_letter", "b1_2.s.write_formal_email"),
    ("b1_1.s.express_opinions", "b1_2.s.participate_discussion"),
    ("b1_1.s.write_structured_paragraph", "b2_1.s.write_essay"),
    ("b1_2.s.tell_story_detail", "b2_2.s.discuss_complex_topics"),
    ("b1_2.s.summarize_text", "b2_2.s.read_authentic_texts"),
    ("b2_1.s.present_argument", "b2_2.s.discuss_complex_topics"),
    ("b2_1.s.write_essay", "b2_2.s.write_report"),
    ("b2_1.s.negotiate", "b2_2.s.mediate_conversation"),
    ("b2_2.s.write_report", "c1_1.s.write_academic_text"),
    ("b2_2.s.discuss_complex_topics", "c1_1.s.present_complex_ideas"),
    ("b1_1.s.understand_main_points", "b2_1.s.understand_extended_speech"),
    ("b2_1.s.understand_extended_speech", "c1_1.s.understand_implicit"),
    ("c1_1.s.write_academic_text", "c1_2.s.write_persuasive_text"),
    ("c1_1.s.present_complex_ideas", "c1_2.s.deliver_spontaneous_speech"),
    ("c1_1.s.understand_implicit", "c1_2.s.critique_text"),
    ("c1_2.s.write_persuasive_text", "c2_1.s.write_publishable"),
    ("c1_2.s.deliver_spontaneous_speech", "c2_1.s.extended_monologue"),
    ("c1_2.s.reformulate_ideas", "c2_1.s.simultaneous_mediation"),
    ("c2_1.s.write_publishable", "c2_2.s.write_any_genre"),
    ("c2_1.s.adapt_any_audience", "c2_2.s.teach_language"),
    ("c2_1.s.interpret_subtlety", "c2_2.s.translate_interpret"),
    ("c1_2.s.follow_complex_interaction", "c2_1.s.simultaneous_mediation"),
    ("c2_1.s.extended_monologue", "c2_2.s.native_fluency"),
]

# ============================================================
# LANGUAGE-SPECIFIC OVERRIDES
# ============================================================
# Each override: {"add_nodes": [...], "remove_nodes": [...], "add_edges": [...]}

LANG_OVERRIDES = {
    "de": {
        "add_nodes": [
            ("a1_1", "k", "noun_gender_cases", "Noun Gender and Cases (Nominative)", ["grammar"]),
            ("a1_2", "k", "accusative_case", "Accusative Case", ["grammar"]),
            ("a2_1", "k", "dative_case", "Dative Case", ["grammar"]),
            ("a2_1", "k", "separable_verbs", "Separable Verbs", ["grammar", "verbs"]),
            ("b1_1", "k", "genitive_case", "Genitive Case", ["grammar"]),
            ("b1_2", "k", "konjunktiv_ii", "Konjunktiv II (Subjunctive)", ["grammar"]),
        ],
        "add_edges": [
            ("a1_1.k.basic_nouns", "a1_1.k.noun_gender_cases"),
            ("a1_1.k.noun_gender_cases", "a1_2.k.accusative_case"),
            ("a1_2.k.accusative_case", "a2_1.k.dative_case"),
            ("a1_2.k.present_simple_regular", "a2_1.k.separable_verbs"),
            ("a2_1.k.dative_case", "b1_1.k.genitive_case"),
            ("b1_2.k.second_conditional", "b1_2.k.konjunktiv_ii"),
            ("a1_1.k.noun_gender_cases", "a1_2.s.describe_objects_people"),
            ("a2_1.k.separable_verbs", "a2_1.s.narrate_past_events"),
        ],
    },
    "es": {
        "add_nodes": [
            ("a1_1", "k", "noun_gender_agreement", "Noun Gender and Agreement", ["grammar"]),
            ("a2_1", "k", "ser_estar", "Ser vs Estar", ["grammar", "verbs"]),
            ("b1_1", "k", "subjuntivo_present", "Present Subjunctive", ["grammar"]),
            ("a2_1", "k", "preterito_imperfecto", "Preterite vs Imperfect", ["grammar", "verbs"]),
        ],
        "add_edges": [
            ("a1_1.k.basic_nouns", "a1_1.k.noun_gender_agreement"),
            ("a1_1.k.noun_gender_agreement", "a1_2.k.basic_adjectives"),
            ("a1_1.k.present_simple_be", "a2_1.k.ser_estar"),
            ("a2_1.k.past_simple", "a2_1.k.preterito_imperfecto"),
            ("a2_2.k.modal_verbs_basic", "b1_1.k.subjuntivo_present"),
            ("b1_1.k.subjuntivo_present", "b1_1.s.express_opinions"),
        ],
    },
    "fr": {
        "add_nodes": [
            ("a1_1", "k", "noun_gender_agreement", "Noun Gender and Agreement", ["grammar"]),
            ("a2_1", "k", "passe_compose_imparfait", "Pass\u00e9 Compos\u00e9 vs Imparfait", ["grammar", "verbs"]),
            ("b1_1", "k", "subjonctif_present", "Present Subjunctive", ["grammar"]),
            ("a1_2", "k", "partitive_articles", "Partitive Articles (du, de la)", ["grammar"]),
        ],
        "add_edges": [
            ("a1_1.k.basic_nouns", "a1_1.k.noun_gender_agreement"),
            ("a1_1.k.noun_gender_agreement", "a1_2.k.articles_demonstratives"),
            ("a1_2.k.articles_demonstratives", "a1_2.k.partitive_articles"),
            ("a2_1.k.past_simple", "a2_1.k.passe_compose_imparfait"),
            ("a2_2.k.modal_verbs_basic", "b1_1.k.subjonctif_present"),
            ("a1_2.k.partitive_articles", "a2_1.k.countable_uncountable"),
        ],
    },
    "ar": {
        "add_nodes": [
            ("a1_1", "k", "arabic_script", "Arabic Script (28 Letters)", ["script"]),
            ("a1_1", "k", "script_direction", "Right-to-Left Writing", ["script"]),
            ("a1_2", "k", "diacritics_vowels", "Short Vowels (Harakat)", ["phonology"]),
            ("a1_2", "k", "root_pattern_system", "3-Letter Root System", ["grammar"]),
            ("a2_1", "k", "dual_number", "Dual Number", ["grammar"]),
            ("a2_1", "k", "case_endings", "Case Endings (I'rab)", ["grammar"]),
            ("b1_1", "k", "verb_forms", "Verb Forms (I-X)", ["grammar", "verbs"]),
        ],
        "remove_nodes": ["alphabet_phonics"],
        "add_edges": [
            ("a1_1.k.arabic_script", "a1_1.k.script_direction"),
            ("a1_1.k.arabic_script", "a1_1.s.copy_words"),
            ("a1_1.k.script_direction", "a1_2.k.diacritics_vowels"),
            ("a1_2.k.diacritics_vowels", "a1_2.k.root_pattern_system"),
            ("a1_2.k.root_pattern_system", "a2_1.k.past_simple"),
            ("a1_1.k.basic_nouns", "a2_1.k.dual_number"),
            ("a2_1.k.dual_number", "a2_1.k.case_endings"),
            ("a1_2.k.root_pattern_system", "b1_1.k.verb_forms"),
            ("b1_1.k.verb_forms", "b1_1.s.express_opinions"),
        ],
    },
    "fa": {
        "add_nodes": [
            ("a1_1", "k", "persian_script", "Persian Script (32 Letters)", ["script"]),
            ("a1_1", "k", "script_direction", "Right-to-Left Writing", ["script"]),
            ("a1_2", "k", "ezafe_construction", "Ezafe Construction", ["grammar"]),
            ("a2_1", "k", "compound_verbs", "Compound Verbs", ["grammar", "verbs"]),
        ],
        "remove_nodes": ["alphabet_phonics"],
        "add_edges": [
            ("a1_1.k.persian_script", "a1_1.k.script_direction"),
            ("a1_1.k.persian_script", "a1_1.s.copy_words"),
            ("a1_1.k.script_direction", "a1_2.k.ezafe_construction"),
            ("a1_2.k.ezafe_construction", "a1_2.s.describe_objects_people"),
            ("a1_2.k.present_simple_regular", "a2_1.k.compound_verbs"),
            ("a2_1.k.compound_verbs", "a2_1.s.narrate_past_events"),
        ],
    },
    "ja": {
        "add_nodes": [
            ("a1_1", "k", "hiragana", "Hiragana (46 Characters)", ["script"]),
            ("a1_1", "k", "katakana", "Katakana (46 Characters)", ["script"]),
            ("a1_2", "k", "kanji_basic", "Basic Kanji (80 Characters)", ["script"]),
            ("a1_1", "k", "particles_basic", "Basic Particles (wa, ga, wo, ni)", ["grammar"]),
            ("a1_2", "k", "counters_classifiers", "Counters and Classifiers", ["grammar"]),
            ("b1_1", "k", "keigo_politeness", "Keigo (Politeness Levels)", ["pragmatics"]),
            ("a2_1", "k", "te_form", "Te-form and Connections", ["grammar", "verbs"]),
        ],
        "remove_nodes": ["alphabet_phonics", "articles_demonstratives"],
        "add_edges": [
            ("a1_1.k.hiragana", "a1_1.k.katakana"),
            ("a1_1.k.hiragana", "a1_1.s.copy_words"),
            ("a1_1.k.hiragana", "a1_1.k.particles_basic"),
            ("a1_1.k.particles_basic", "a1_1.s.ask_yes_no"),
            ("a1_1.k.katakana", "a1_2.k.kanji_basic"),
            ("a1_1.k.numbers_1_20", "a1_2.k.counters_classifiers"),
            ("a1_2.k.counters_classifiers", "a1_2.s.order_food"),
            ("a1_2.k.present_simple_regular", "a2_1.k.te_form"),
            ("a2_1.k.te_form", "a2_1.s.make_suggestions"),
            ("b1_1.k.connectors_discourse", "b1_1.k.keigo_politeness"),
            ("b1_1.k.keigo_politeness", "b1_1.s.handle_travel_situations"),
        ],
    },
    "ko": {
        "add_nodes": [
            ("a1_1", "k", "hangul", "Hangul Alphabet", ["script"]),
            ("a1_1", "k", "particles_markers", "Topic/Subject/Object Particles", ["grammar"]),
            ("a1_2", "k", "honorific_system", "Honorific System (Formal/Informal)", ["pragmatics"]),
            ("a2_1", "k", "verb_conjugation_patterns", "Verb Conjugation Patterns", ["grammar", "verbs"]),
        ],
        "remove_nodes": ["alphabet_phonics", "articles_demonstratives"],
        "add_edges": [
            ("a1_1.k.hangul", "a1_1.s.copy_words"),
            ("a1_1.k.hangul", "a1_1.k.particles_markers"),
            ("a1_1.k.particles_markers", "a1_1.s.ask_yes_no"),
            ("a1_1.k.personal_pronouns", "a1_2.k.honorific_system"),
            ("a1_2.k.honorific_system", "a1_2.s.order_food"),
            ("a1_2.k.present_simple_regular", "a2_1.k.verb_conjugation_patterns"),
            ("a2_1.k.verb_conjugation_patterns", "a2_1.s.narrate_past_events"),
        ],
    },
    "zh": {
        "add_nodes": [
            ("a1_1", "k", "pinyin", "Pinyin Romanization", ["phonology"]),
            ("a1_1", "k", "tones", "Four Tones", ["phonology"]),
            ("a1_2", "k", "characters_basic", "Basic Characters (200)", ["script"]),
            ("a1_2", "k", "radicals_strokes", "Radicals and Stroke Order", ["script"]),
            ("a1_2", "k", "measure_words", "Measure Words (Classifiers)", ["grammar"]),
            ("a2_1", "k", "aspect_particles", "Aspect Particles (le, guo, zhe)", ["grammar"]),
        ],
        "remove_nodes": ["alphabet_phonics", "articles_demonstratives", "past_simple", "future_forms",
                         "present_perfect", "past_perfect", "present_simple_regular"],
        "add_nodes_extra": [
            ("a1_2", "k", "basic_verb_patterns", "Basic Verb Patterns", ["grammar", "verbs"]),
            ("a2_1", "k", "complement_structures", "Complement Structures", ["grammar"]),
        ],
        "add_edges": [
            ("a1_1.k.pinyin", "a1_1.k.tones"),
            ("a1_1.k.pinyin", "a1_1.s.copy_words"),
            ("a1_1.k.tones", "a1_2.k.characters_basic"),
            ("a1_2.k.characters_basic", "a1_2.k.radicals_strokes"),
            ("a1_1.k.numbers_1_20", "a1_2.k.measure_words"),
            ("a1_2.k.measure_words", "a1_2.s.order_food"),
            ("a1_2.k.basic_verb_patterns", "a2_1.k.aspect_particles"),
            ("a2_1.k.aspect_particles", "a2_1.s.narrate_past_events"),
            ("a1_2.k.basic_verb_patterns", "a2_1.k.complement_structures"),
            ("a2_1.k.complement_structures", "a2_1.s.make_suggestions"),
            ("a1_1.k.present_simple_be", "a1_2.k.basic_verb_patterns"),
        ],
    },
    "ru": {
        "add_nodes": [
            ("a1_1", "k", "cyrillic_alphabet", "Cyrillic Alphabet (33 Letters)", ["script"]),
            ("a1_2", "k", "case_system_basic", "Case System (Nominative/Accusative)", ["grammar"]),
            ("a2_1", "k", "case_system_full", "Case System (6 Cases)", ["grammar"]),
            ("a2_1", "k", "verb_aspect", "Verb Aspect (Perfective/Imperfective)", ["grammar", "verbs"]),
            ("b1_1", "k", "verbs_of_motion", "Verbs of Motion", ["grammar", "verbs"]),
        ],
        "remove_nodes": ["alphabet_phonics", "articles_demonstratives"],
        "add_edges": [
            ("a1_1.k.cyrillic_alphabet", "a1_1.s.copy_words"),
            ("a1_1.k.basic_nouns", "a1_2.k.case_system_basic"),
            ("a1_2.k.case_system_basic", "a2_1.k.case_system_full"),
            ("a1_2.k.present_simple_regular", "a2_1.k.verb_aspect"),
            ("a2_1.k.verb_aspect", "a2_1.s.narrate_past_events"),
            ("a2_1.k.case_system_full", "b1_1.k.verbs_of_motion"),
            ("b1_1.k.verbs_of_motion", "b1_1.s.handle_travel_situations"),
        ],
    },
    "tr": {
        "add_nodes": [
            ("a1_1", "k", "vowel_harmony", "Vowel Harmony", ["phonology"]),
            ("a1_1", "k", "agglutination", "Agglutination Basics", ["grammar"]),
            ("a1_2", "k", "case_suffixes", "Case Suffixes", ["grammar"]),
            ("a2_1", "k", "verbal_nouns", "Verbal Nouns and Nominalisation", ["grammar"]),
        ],
        "remove_nodes": ["articles_demonstratives"],
        "add_edges": [
            ("a1_1.k.alphabet_phonics", "a1_1.k.vowel_harmony"),
            ("a1_1.k.vowel_harmony", "a1_1.k.agglutination"),
            ("a1_1.k.agglutination", "a1_2.k.case_suffixes"),
            ("a1_2.k.case_suffixes", "a1_2.s.ask_where_when"),
            ("a1_2.k.present_simple_regular", "a2_1.k.verbal_nouns"),
        ],
    },
    "ms": {
        "add_nodes": [
            ("a1_2", "k", "affixation_me_ber", "Affixation (me-, ber-, pe-)", ["grammar"]),
            ("a2_1", "k", "reduplication", "Reduplication", ["grammar"]),
        ],
        "remove_nodes": ["articles_demonstratives", "present_simple_be"],
        "add_nodes_extra": [
            ("a1_1", "k", "basic_sentence_svo", "Basic SVO Sentence Structure", ["grammar"]),
        ],
        "add_edges": [
            ("a1_1.k.basic_sentence_svo", "a1_1.s.introduce_self"),
            ("a1_1.k.basic_sentence_svo", "a1_1.s.ask_yes_no"),
            ("a1_1.k.basic_sentence_svo", "a1_2.k.affixation_me_ber"),
            ("a1_2.k.affixation_me_ber", "a1_2.s.describe_objects_people"),
            ("a1_2.k.affixation_me_ber", "a2_1.k.reduplication"),
            ("a1_1.k.personal_pronouns", "a1_1.k.basic_sentence_svo"),
        ],
    },
    # English and default — no overrides needed
    "en": {},
}

# ============================================================
# LANGUAGE DEFINITIONS
# ============================================================
LANGUAGES = {
    "en": {"name": "English", "native": "English", "flag": "🇬🇧"},
    "ms": {"name": "Bahasa Malaysia", "native": "Bahasa Malaysia", "flag": "🇲🇾"},
    "de": {"name": "German", "native": "Deutsch", "flag": "🇩🇪"},
    "fa": {"name": "Farsi", "native": "فارسی", "flag": "🇮🇷"},
    "ar": {"name": "Arabic", "native": "العربية", "flag": "🇸🇦"},
    "es": {"name": "Spanish", "native": "Español", "flag": "🇪🇸"},
    "fr": {"name": "French", "native": "Français", "flag": "🇫🇷"},
    "ru": {"name": "Russian", "native": "Русский", "flag": "🇷🇺"},
    "ja": {"name": "Japanese", "native": "日本語", "flag": "🇯🇵"},
    "ko": {"name": "Korean", "native": "한국어", "flag": "🇰🇷"},
    "tr": {"name": "Turkish", "native": "Türkçe", "flag": "🇹🇷"},
    "zh": {"name": "Mandarin Chinese", "native": "中文", "flag": "🇨🇳"},
}


def generate_language(lang_code):
    lang = LANGUAGES[lang_code]
    overrides = LANG_OVERRIDES.get(lang_code, {})

    # Build node list
    remove_slugs = set(overrides.get("remove_nodes", []))
    nodes = []
    node_ids = set()

    for level, tp, slug, label, tags in TEMPLATE_NODES:
        if slug in remove_slugs:
            continue
        nid = f"{lang_code}.{level}.{tp}.{slug}"
        book_id = f"book.{level}"
        b = BOOK_MAP[book_id]
        ntype = "concept" if tp == "k" else "technique"
        nodes.append({
            "id": nid, "label": label, "type": ntype,
            "description": f"{label} — {b['name']}",
            "grade_range": [level.upper().replace("_", ".")],
            "tags": [("knowledge" if tp == "k" else "skill")] + tags,
            "pages": "", "book": book_id,
            "bookName": b["name"], "bookColor": b["color"], "bookOrder": b["order"],
        })
        node_ids.add(nid)

    # Add language-specific nodes
    for level, tp, slug, label, tags in overrides.get("add_nodes", []) + overrides.get("add_nodes_extra", []):
        nid = f"{lang_code}.{level}.{tp}.{slug}"
        book_id = f"book.{level}"
        b = BOOK_MAP[book_id]
        ntype = "concept" if tp == "k" else "technique"
        nodes.append({
            "id": nid, "label": label, "type": ntype,
            "description": f"{label} — {b['name']}",
            "grade_range": [level.upper().replace("_", ".")],
            "tags": [("knowledge" if tp == "k" else "skill")] + tags,
            "pages": "", "book": book_id,
            "bookName": b["name"], "bookColor": b["color"], "bookOrder": b["order"],
        })
        node_ids.add(nid)

    # Build edge list
    edges = []
    edge_set = set()

    for src_slug, tgt_slug in TEMPLATE_EDGES:
        src = f"{lang_code}.{src_slug}"
        tgt = f"{lang_code}.{tgt_slug}"
        if src in node_ids and tgt in node_ids and (src, tgt) not in edge_set:
            edges.append({"source": src, "target": tgt, "relation": "prerequisite_for"})
            edge_set.add((src, tgt))

    for src_slug, tgt_slug in overrides.get("add_edges", []):
        src = f"{lang_code}.{src_slug}"
        tgt = f"{lang_code}.{tgt_slug}"
        if src in node_ids and tgt in node_ids and (src, tgt) not in edge_set:
            edges.append({"source": src, "target": tgt, "relation": "prerequisite_for"})
            edge_set.add((src, tgt))

    # Validate: no orphans
    connected = set()
    for e in edges:
        connected.add(e["source"])
        connected.add(e["target"])
    orphans = [n["id"] for n in nodes if n["id"] not in connected]

    # Validate: DAG
    adj = defaultdict(list)
    for e in edges:
        adj[e["source"]].append(e["target"])
    in_deg = defaultdict(int)
    for e in edges:
        in_deg[e["target"]] += 1
    q = deque([n["id"] for n in nodes if in_deg[n["id"]] == 0])
    visited = 0
    while q:
        u = q.popleft()
        visited += 1
        for v in adj[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                q.append(v)
    is_dag = visited == len(nodes)

    # Build output
    output = {
        "metadata": {
            "domain": "language_learning",
            "curriculum": "CEFR",
            "language": lang["name"],
            "language_code": lang_code,
            "version": "0.1.0",
            "description": f"{lang['name']} ({lang['native']}) — CEFR A1.1 to C2.2",
            "sources": ["CEFR Companion Volume (2020)", "Council of Europe"],
            "last_updated": "2026-03-27",
        },
        "books": BOOKS,
        "nodes": nodes,
        "edges": edges,
    }

    outpath = os.path.join(DATA_DIR, f"lang-{lang_code}.json")
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)

    status = "OK" if (is_dag and len(orphans) == 0) else f"ISSUES: orphans={len(orphans)}, dag={is_dag}"
    print(f"  {lang_code} ({lang['name']}): {len(nodes)} nodes, {len(edges)} edges — {status}")
    if orphans:
        for o in orphans[:5]:
            print(f"    orphan: {o}")

    return len(nodes), len(edges)


if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(LANGUAGES.keys())
    total_n, total_e = 0, 0
    for code in targets:
        if code not in LANGUAGES:
            print(f"Unknown language: {code}")
            continue
        n, e = generate_language(code)
        total_n += n
        total_e += e
    print(f"\nTotal: {len(targets)} languages, {total_n} nodes, {total_e} edges")
