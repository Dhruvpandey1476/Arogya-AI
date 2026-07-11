from fastapi import APIRouter, Request

router = APIRouter()


@router.get("")
async def health_check(request: Request):
    models = request.app.state.models
    return {
        "status": "ok",
        "models": {
            "disease_predictor": models.get("disease_predictor") is not None,
            "severity_classifier": models.get("severity_classifier") is not None,
            "skin_classifier": models.get("skin_classifier") is not None,
            "rag_retriever": models.get("rag_retriever") is not None,
            "symptom_embedder": models.get("symptom_embedder") is not None,
        }
    }
