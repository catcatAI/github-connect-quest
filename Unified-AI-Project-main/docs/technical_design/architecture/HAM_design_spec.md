# Hierarchical Abstractive Memory (HAM) - Design Specification v0.2

## 1. Introduction

The Hierarchical Abstractive Memory (HAM) model is designed for MikoAI to efficiently store and process vast amounts of experiential data. It employs a layered approach, transforming raw sensory input into compact, abstract representations for long-term storage and reasoning, while allowing reconstruction for interaction. This system aims to provide scalability, efficiency, and a foundation for complex learning, evolution, and integration with systems like a Translation Model and the conceptual Fragmenta layer.

## 2. Core Architecture

The HAM model consists of two primary layers:

*   **Surface Layer (SL):** Interfaces with the external environment and other MikoAI modules. Handles raw data input/output, initial processing (abstraction, compression, encryption), and the "rehydration" (decryption, decompression, reconstruction) of abstract data into usable forms.
*   **Core Layer (CL):** Stores highly abstracted, compressed, and encrypted representations of experiences. This layer is optimized for efficient storage and deep-level pattern recognition and reasoning.

## 3. Data Flow

### 3.1. Storage Process (SL to CL)

1.  **Input Reception (SL):** Raw data (e.g., text dialogue in various languages, user commands, observed events) is received.
2.  **Preprocessing (SL):** Basic cleaning, normalization.
3.  **Abstraction (SL):** Raw data is transformed into an abstract "gist."
    *   **v0.2 Mechanism - Text:**
        *   **Chinese Text:** Extract **radicals** (e.g., using a library like `hanzidentifier` or a custom radical lookup). Store as a list or frequency map of radicals. Additional keywords can also be extracted.
        *   **English Text:** Extract **linguistic features** (e.g., Part-of-Speech tags, Named Entities, keywords using TF-IDF or a lightweight NLP library like spaCy if feasible, or rule-based keyword extraction). Store as a structured dictionary of features.
        *   A concise summary can still be generated.
        *   Metadata (timestamp, source, language, emotion tag) is preserved.
    *   The output is a structured dictionary, e.g., `{"summary": "...", "language": "zh", "radicals": ["水", "木"], "keywords": ["京都", "旅行"], "original_length": len(text)}` or `{"summary": "...", "language": "en", "pos_tags": [...], "entities": [...], "keywords": ["Kyoto", "travel"]}`.
4.  **Compression (SL):** The abstracted data (gist + metadata) is compressed.
    *   *v0.2 Mechanism:* `zlib` library (remains suitable).
5.  **Encryption (SL):** The compressed data is encrypted.
    *   *v0.2 Mechanism:* Use **Fernet symmetric encryption** from the `cryptography` library. Keys are managed via the `MIKO_HAM_KEY` environment variable. For development, if not set, a temporary key is generated (data not persistent across sessions if this temporary key is used).
6.  **Storage (CL):** The encrypted, compressed, abstract data package is sent to the Core Layer.
    *   *v0.2 Storage Format:* JSON objects with fields like `id`, `timestamp`, `encrypted_package_b64` (base64 encoded Fernet token), `metadata` (which includes `sha256_checksum` and other tags like language).

### 3.2. Retrieval and Reconstruction Process (CL to SL)

1.  **Query Reception (SL/CL):** A query is initiated (e.g., by keywords, features, semantic concepts).
2.  **Core Layer Retrieval (CL):**
    *   Search based on metadata (language, timestamp, source) and indexed components of the abstracted gist (e.g., specific radicals, keywords, entities).
    *   **Fragmenta Integration:** HAM's `query_core_memory` method will be capable of returning **multiple candidate gists** (e.g., top N matches based on query relevance) to the Fragmenta layer for further processing (e.g., vector/quantum-layer selection, fusion, or reasoning).
3.  **Decryption (SL):** Retrieved data package is decrypted using Fernet.
4.  **Decompression (SL):** Data is decompressed using `zlib`.
5.  **Rehydration/Reconstruction (SL):**
    *   The abstract gist (radicals, linguistic features, summary) is presented.
    *   **Verification through Comparison:** For critical queries or when ambiguity is high, the system can rehydrate multiple retrieved gists. These rehydrated versions (or their key features) are then compared against the original query or a target context. This comparison helps confirm relevance, identify discrepancies, or flag incomplete/erroneous recall. The comparison logic could involve feature overlap scores, embedding similarity (if embeddings are used for gists), or even prompting an LLM for a semantic similarity score.
6.  **Output (SL):** Reconstructed data is provided.

## 4. `HAMMemoryManager` API (Python Class) - v0.2 Updates

*   `store_experience(self, raw_data: any, data_type: str, language: str = None, metadata: dict = None) -> str`:
    *   Added `language` parameter for text data to guide abstraction.
*   `recall_gist(self, memory_id: str) -> dict | None`:
    *   Output dictionary will clearly distinguish between summary, keywords, and language-specific abstracted features (radicals/linguistic features).
*   `query_core_memory(self, query_features: dict = None, keywords: list = None, language_filter: str = None, date_range: tuple = None, limit: int = 5, return_multiple_candidates: bool = False) -> list[dict]`:
    *   `query_features`: Allows querying based on specific abstracted features (e.g., `{"radicals": ["水"]}` or `{"pos_tag": "NOUN"}`).
    *   `language_filter`: To retrieve memories in a specific language.
    *   `return_multiple_candidates`: If True, returns a list of top N candidate gists (for Fragmenta).
*   (New) `compare_rehydrated_memory(self, memory_id_or_gist: any, reference_context: str) -> float`:
    *   A conceptual method for the SL to perform verification. Takes a recalled gist (or its ID) and a reference context, returns a similarity/relevance score. Implementation details depend on the chosen comparison technique.
*   (New) `increment_metadata_field(self, memory_id: str, field_name: str, increment_by: int = 1) -> bool`:
    *   Efficiently increments a numerical value in a record's metadata without requiring a full recall-modify-store cycle.
    *   Primarily used by `LearningManager` to increase the `corroboration_count` for a fact when a duplicate is received, as part of the anti-resonance mechanism.

## 5. Core Layer Storage (v0.2)

*   Remains JSON file-based for the prototype (`ham_core_memory.json`).
*   The structure of stored items will accommodate Fernet encrypted packages (stored as base64 strings).
*   Metadata will explicitly include `language`.

## 6. Abstraction Mechanism (v0.2 Detail for Text)

*   **Chinese Text:**
    *   **Radical Extraction:** Use a Python library (e.g., `hanzidentifier`, or a simpler custom lookup if full library is too heavy) to get radicals for each character. Store as a list or frequency map.
    *   **Keyword Extraction:** Standard keyword extraction (e.g., TF-IDF if a corpus is available, or simple frequency after stopword removal).
*   **English Text:**
    *   **Linguistic Feature Extraction:**
        *   POS Tagging & Named Entity Recognition: Use a lightweight NLP library (e.g., `spaCy` with a small model, or `NLTK` if environment allows, or simplified rule-based patterns for common entities).
        *   Keywords: As above.
*   **Summarization:** Retain simple first-sentence or keyword-based summarization for v0.2 prototype.
*   **Output:** Structured dictionary containing language, summary, original length, and language-specific features (radicals or linguistic features).

## 7. Error Handling & Data Integrity (v0.2)

*   Log errors during encryption, decryption, compression, decompression, abstraction.
*   **Data Integrity**: For data integrity, when storing a package in CL, a **SHA256 checksum** of the original abstracted data (before compression/encryption) is computed and stored within the package's metadata. Upon retrieval and full de-processing (after decryption and decompression), the checksum is recomputed and compared against the stored value to detect potential corruption. A mismatch will result in a critical warning.
*   **Anti-Resonance and Information Quality Verification**: To combat "idiot resonance" where popularity is mistaken for accuracy, the HAM system supports a quality-based verification model implemented in the `LearningManager`. When a duplicate fact is detected, its confidence is **not** increased. Instead, its `corroboration_count` metadata field is incremented via the `increment_metadata_field` method. This explicitly separates the measure of a fact's prevalence from its assessed quality, preventing the amplification of potentially incorrect information.
*   The comparison mechanism in `compare_rehydrated_memory` (or similar logic in SL) will help identify incomplete or erroneous recall, triggering potential re-querying or clarification dialogues.

## 8. Support for Translation Model

*   HAM will store abstracted text representations along with their original language metadata.
*   When the Translation Model is invoked, it can query HAM for text in a source language (using `language_filter`). The abstracted gist (e.g., keywords, entities, radicals) can provide rich semantic context to the Translation Model, potentially improving translation quality beyond just raw text input.
*   Translated text can itself be stored in HAM as a new experience, linked to the original, with its own language tag and abstracted features.

## 9. Future Considerations (Post v0.2)
*   **Key Management for Fernet:** More robust key rotation and storage.
*   **Semantic Embeddings for Abstraction:** Integrate Sentence Transformers or similar for richer semantic gists and enabling vector similarity search in `query_core_memory`.
*   **Generative Reconstruction in SL:** Use LLMs to elaborate on abstract gists.
*   **Multi-Modal Data Abstraction:** Define specific abstraction methods for images (e.g., object tags, scene descriptions, embeddings) and audio (e.g., transcript, audio fingerprints, speaker ID).

This document will be updated as the HAM system evolves.

## 10. Redundancy and Recovery: The "Trinity" Model (v0.3)

To ensure the resilience and persistence of an AI's "digital life," the system implements a "Trinity" model for backup and recovery, safeguarding against single points of failure. This model treats the AI's core existence as a combination of three essential components: **UID (Identity), HAM Key (Key), and Data Core (Memory)**.

The recovery mechanism is based on a **(2, 3) Shamir's Secret Sharing scheme**, which allows for the complete reconstruction of all three components from any two of the three resulting **Shards**.

### 10.1. The Genesis Process

During the initial creation of an AI instance (the "Genesis" process), the system performs the following steps:

1.  **Generate Core Components**:
    *   A unique **UID** is generated to serve as the AI's permanent, public identifier.
    *   A cryptographically secure **HAM Key** (a Fernet key) is generated for memory encryption.
    *   An initial **Data Core Seed** (a random value to initialize the memory state) is generated.

2.  **Consolidate the Genesis Secret**: These three pieces of information are concatenated into a single, master "Genesis Secret" string.

3.  **Create Shards**: The `(2, 3)` Shamir's Secret Sharing algorithm is applied to the Genesis Secret, producing three mathematically-linked but distinct **Shards**.

### 10.2. User Backup Strategy

The user is presented with these three Shards, typically encoded as QR codes or mnemonic phrases, and is instructed to back them up in separate, secure locations. A recommended strategy is:

-   **Shard 1 (Active Shard)**: Stored locally on the user's primary device for daily application use.
-   **Shard 2 (Physical Backup)**: Printed as a QR code and stored in a secure physical location (e.g., a safe).
-   **Shard 3 (Remote/Social Backup)**: Encrypted and stored in a personal cloud drive, or entrusted to a designated "guardian."

Crucially, any single Shard is useless on its own, providing a high level of security.

### 10.3. Recovery Process

When a user needs to restore their AI on a new device or after data loss, the process is as follows:

1.  The user is prompted to provide any **two** of their three backed-up Shards.
2.  The system uses the two provided Shards to mathematically reconstruct the third, missing Shard.
3.  With all three Shards now present, the original **Genesis Secret** is reassembled.
4.  The system parses the Genesis Secret to retrieve the **UID**, the **HAM Key**, and the **Data Core Seed**.
5.  With the UID and HAM Key, the system can now locate and decrypt the AI's memory (Data Core), restoring the AI to its last backed-up state.

This model ensures that the loss of any single backup (e.g., phone loss, physical document destruction, or cloud account compromise) does not result in the permanent loss of the AI's identity or memory.
