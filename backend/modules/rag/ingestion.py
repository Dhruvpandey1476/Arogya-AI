"""
Medical document ingestion script for ChromaDB.
Run this BEFORE the hackathon.

This script:
1. Loads medical documents from data/raw/medical_docs/
2. Chunks them into 300-token passages
3. Embeds with sentence-transformers
4. Stores in ChromaDB for RAG retrieval

Also includes built-in medical knowledge if no docs are found.
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys
import uuid
import re

sys.path.append(str(Path(__file__).parent.parent.parent))
import config

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


BUILTIN_MEDICAL_KNOWLEDGE = [
    {
        "text": "Malaria is caused by Plasmodium parasites transmitted through the bites of infected female Anopheles mosquitoes. Symptoms include fever, chills, headache, muscle pain, fatigue, nausea, and vomiting. High fever typically occurs in cycles. Treatment involves antimalarial medications prescribed by a doctor. Prevention includes mosquito nets, repellents, and prophylactic medication when traveling to endemic areas.",
        "source": "WHO Malaria Fact Sheet"
    },
    {
        "text": "Dengue fever is a mosquito-borne viral infection causing severe flu-like illness. Symptoms include sudden high fever, severe headache, pain behind eyes, muscle and joint pain, nausea, vomiting, swollen glands, and rash. Severe dengue can cause serious bleeding, organ impairment, and plasma leaking. There is no specific treatment; management includes rest, fluids, and pain relievers. Avoid aspirin and ibuprofen as they can worsen bleeding.",
        "source": "WHO Dengue Guidelines"
    },
    {
        "text": "Typhoid fever is a bacterial infection caused by Salmonella typhi spread through contaminated food and water. Symptoms develop gradually: sustained fever up to 40°C, weakness, stomach pain, headache, diarrhea or constipation, and rose-colored spots on chest. Treatment requires antibiotics prescribed by a doctor. Prevention involves safe food and water practices and vaccination.",
        "source": "WHO Typhoid Guidelines"
    },
    {
        "text": "Diabetes mellitus is a chronic disease that occurs when the pancreas does not produce enough insulin or when the body cannot effectively use the insulin it produces. Type 1 diabetes requires daily insulin administration. Type 2 diabetes can often be managed with lifestyle changes, oral medications, and insulin. Symptoms include excessive thirst, frequent urination, blurred vision, fatigue, and slow wound healing. Long-term complications affect heart, kidneys, eyes, and nerves.",
        "source": "WHO Diabetes Fact Sheet"
    },
    {
        "text": "Hypertension (high blood pressure) is when blood pressure is consistently 140/90 mmHg or higher. It is called a silent killer because it often has no symptoms. Risk factors include unhealthy diet, physical inactivity, tobacco use, obesity, and family history. It can lead to heart attack, stroke, kidney disease, and vision loss. Management includes lifestyle modification, reduced salt intake, exercise, and antihypertensive medications.",
        "source": "WHO Hypertension Guidelines"
    },
    {
        "text": "Pneumonia is an infection that inflames air sacs in one or both lungs, which may fill with fluid or pus. Symptoms include cough with phlegm or pus, fever, chills, and difficulty breathing. Bacteria, viruses, and fungi can all cause pneumonia. Bacterial pneumonia is treated with antibiotics. Rest, adequate fluids, and fever reducers help manage symptoms. Hospitalization may be needed for severe cases, elderly patients, or young children.",
        "source": "MedlinePlus Pneumonia"
    },
    {
        "text": "Jaundice is yellowing of the skin and whites of the eyes caused by excess bilirubin in blood. Causes include liver disease (hepatitis, cirrhosis), bile duct obstruction, hemolytic anemia, and Gilbert syndrome. Symptoms include yellow skin and eyes, dark urine, pale stools, fatigue, and abdominal pain. Treatment targets the underlying cause. Liver function tests and ultrasound help diagnose the cause.",
        "source": "MedlinePlus Jaundice"
    },
    {
        "text": "Gastroenteritis, often called stomach flu, is inflammation of the stomach and intestines. Symptoms include diarrhea, nausea, vomiting, stomach cramps, and sometimes fever. Most cases are caused by viruses like norovirus or rotavirus. Treatment focuses on preventing dehydration by drinking plenty of fluids. Oral rehydration solutions are recommended. Most cases resolve within 1-3 days. Seek medical attention if symptoms are severe or persist.",
        "source": "MedlinePlus Gastroenteritis"
    },
    {
        "text": "Chicken pox (varicella) is a highly contagious infection causing an itchy blister rash. It spreads through direct contact or airborne droplets. The rash starts as red spots that become fluid-filled blisters and then crust over. Other symptoms include fever, fatigue, loss of appetite, and headache. Calamine lotion and antihistamines help with itching. Do not give aspirin to children with chickenpox. The varicella vaccine prevents the disease.",
        "source": "CDC Chickenpox Guidelines"
    },
    {
        "text": "Urinary tract infection (UTI) is an infection in any part of the urinary system. Most infections involve the lower urinary tract — bladder and urethra. Symptoms include burning sensation when urinating, frequent urge to urinate, cloudy or strong-smelling urine, pelvic pain, and low fever. UTIs are treated with antibiotics. Drinking plenty of water helps flush bacteria. Women are more prone to UTIs than men.",
        "source": "MedlinePlus UTI"
    },
    {
        "text": "Common cold is a viral infection of the nose and throat. Rhinovirus is the most common cause. Symptoms include runny or stuffy nose, sore throat, cough, mild fever, sneezing, and mild body aches. There is no cure. Rest, fluids, and over-the-counter medications help manage symptoms. Antibiotics are ineffective against viruses. Most colds resolve within 7-10 days. Wash hands frequently to prevent spread.",
        "source": "CDC Common Cold"
    },
    {
        "text": "Migraine is a neurological condition causing intense, debilitating headaches often with nausea, vomiting, and sensitivity to light and sound. Some migraines are preceded by aura — visual disturbances, numbness, or speech difficulty. Triggers include stress, hormonal changes, certain foods, sleep changes, and sensory stimuli. Treatment includes pain-relief medications, triptans, and preventive medications. Rest in a dark quiet room helps during attacks.",
        "source": "WHO Headache Disorders"
    },
    {
        "text": "Asthma is a chronic condition in which airways narrow and swell and may produce extra mucus. Symptoms include shortness of breath, chest tightness, wheezing, and coughing, especially at night or early morning. Triggers include allergens, air pollution, exercise, respiratory infections, and cold air. Treatment includes rescue inhalers (bronchodilators) for immediate relief and controller medications for long-term management. Avoiding triggers is essential.",
        "source": "WHO Asthma Guidelines"
    },
    {
        "text": "Hepatitis B is a serious liver infection caused by the hepatitis B virus (HBV). It can be acute (short-term) or chronic (long-lasting). Symptoms include jaundice, fatigue, dark urine, nausea, vomiting, and abdominal pain. Chronic hepatitis B can lead to cirrhosis and liver cancer. It spreads through blood, sexual contact, and from mother to child. Vaccination is available and highly effective. Antiviral medications treat chronic infection.",
        "source": "WHO Hepatitis B Guidelines"
    },
    {
        "text": "First aid for fever: measure temperature with a thermometer. For adults, fever above 39.4°C (103°F) warrants medical attention. Cool the person with a lukewarm sponge bath. Encourage fluid intake to prevent dehydration. Paracetamol (acetaminophen) or ibuprofen can reduce fever — follow dosage instructions. Do not give aspirin to children. Seek emergency care for fever above 40°C, severe headache, neck stiffness, confusion, rash, or difficulty breathing.",
        "source": "St. John's Ambulance First Aid"
    },
    {
        "text": "First aid for suspected heart attack: call emergency services immediately. Have the person sit or lie in comfortable position. Loosen tight clothing. If not allergic and conscious, give aspirin 300mg to chew. If trained, be prepared to perform CPR if the person becomes unresponsive. Do not leave the person alone. Do not give food or water. Heart attack symptoms: chest pain radiating to arm/jaw, shortness of breath, sweating, nausea.",
        "source": "St. John's Ambulance First Aid"
    },
    {
        "text": "Dehydration first aid: mild to moderate dehydration can be treated with oral rehydration solution (ORS) — mix 1 liter water with 6 teaspoons sugar and half teaspoon salt. Drink small sips frequently. Avoid sugary drinks, alcohol, and caffeinated beverages. For severe dehydration — sunken eyes, no urination for 8 hours, confusion — seek emergency medical care. Intravenous fluids may be required.",
        "source": "WHO Oral Rehydration Therapy"
    },
    {
        "text": "Skin infections: bacterial skin infections like impetigo present as red sores that rupture and crust over. Fungal infections cause ring-shaped rashes, scaling, and itching. Treatment depends on cause: topical or oral antibiotics for bacterial infections, antifungal creams for fungal infections. Keep affected area clean and dry. Do not share towels or clothing. Seek medical advice if the infection spreads or does not improve within a week.",
        "source": "MedlinePlus Skin Infections"
    },
    {
        "text": "Tuberculosis (TB) is caused by Mycobacterium tuberculosis and primarily affects the lungs. Symptoms include persistent cough lasting 3+ weeks, coughing blood, chest pain, fatigue, fever, night sweats, and weight loss. TB spreads through the air when infected people cough or sneeze. Treatment requires a 6-month course of antibiotics. Incomplete treatment can lead to drug-resistant TB. BCG vaccination provides partial protection in children.",
        "source": "WHO Tuberculosis Fact Sheet"
    },
    {
        "text": "Arthritis causes joint pain, stiffness, and inflammation. Osteoarthritis is the most common type, caused by wear and tear on cartilage. Rheumatoid arthritis is an autoimmune disease. Symptoms include joint pain, swelling, reduced range of motion, and morning stiffness. Management includes pain medications, anti-inflammatory drugs, physical therapy, and in severe cases, joint replacement surgery. Low-impact exercise, maintaining healthy weight, and joint protection strategies help manage symptoms.",
        "source": "MedlinePlus Arthritis"
    },
]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def ingest():
    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(
        path=str(config.CHROMA_DB_PATH),
        settings=Settings(anonymized_telemetry=False),
    )

    # Delete existing collection if it exists
    try:
        client.delete_collection("medical_docs")
        print("Deleted existing collection")
    except Exception:
        pass

    collection = client.create_collection(
        "medical_docs",
        metadata={"hnsw:space": "cosine"},
    )

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    all_chunks = []
    all_sources = []

    # Load from files if available
    docs_path = config.MEDICAL_DOCS_PATH
    if docs_path.exists():
        for doc_file in docs_path.glob("*.txt"):
            with open(doc_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            chunks = chunk_text(content)
            all_chunks.extend(chunks)
            all_sources.extend([doc_file.name] * len(chunks))
            print(f"  Loaded: {doc_file.name} ({len(chunks)} chunks)")

    # Always include built-in knowledge
    for item in BUILTIN_MEDICAL_KNOWLEDGE:
        chunks = chunk_text(item["text"])
        all_chunks.extend(chunks)
        all_sources.extend([item["source"]] * len(chunks))

    print(f"\nTotal chunks to embed: {len(all_chunks)}")

    # Batch embed and insert
    batch_size = 64
    for i in range(0, len(all_chunks), batch_size):
        batch_texts = all_chunks[i:i+batch_size]
        batch_sources = all_sources[i:i+batch_size]
        batch_ids = [str(uuid.uuid4()) for _ in batch_texts]

        embeddings = model.encode(batch_texts, convert_to_numpy=True).tolist()

        collection.add(
            documents=batch_texts,
            embeddings=embeddings,
            metadatas=[{"source": s} for s in batch_sources],
            ids=batch_ids,
        )
        print(f"  Ingested batch {i//batch_size + 1}/{(len(all_chunks)-1)//batch_size + 1}")

    print(f"\nIngestion complete. Total chunks in DB: {collection.count()}")


if __name__ == "__main__":
    ingest()
