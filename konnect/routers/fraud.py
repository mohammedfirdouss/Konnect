"""Fraud detection router"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..dependencies import get_current_active_user
from ..schemas import (
    FraudDetectionSummary,
    FraudDetectionResponse,
)
from ..supabase_client import supabase
from ..agents.fraud_detection import (
    analyze_user_activity,
    analyze_listing_patterns,
    detect_payment_fraud,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fraud", tags=["fraud"])


def create_fraud_report(
    entity_type: str,
    entity_id: int,
    risk_score: float,
    risk_level: str,
    flagged_reasons: List[str],
    detection_method: str,
    confidence: float,
) -> bool:
    """Create a fraud detection report"""
    if not supabase:
        logger.error("Supabase not available for fraud report creation")
        return False

    try:
        report_data = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "flagged_reasons": flagged_reasons,
            "detection_method": detection_method,
            "confidence": confidence,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }

        response = supabase.table("fraud_reports").insert(report_data).execute()

        if response.data:
            logger.info(f"Fraud report created: {response.data[0]['id']}")
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"Error creating fraud report: {e}")
        return False


def check_user_fraud(user_id: int) -> dict:
    """Check user for fraud patterns"""
    try:
        # Analyze user activity
        analysis = analyze_user_activity(user_id)

        if "error" in analysis:
            return analysis

        # Calculate risk score based on analysis
        risk_score = 0.0
        flagged_reasons = []

        # Check for suspicious patterns
        if analysis.get("rapid_listing_creation", False):
            risk_score += 0.3
            flagged_reasons.append("Rapid listing creation detected")

        if analysis.get("unusual_pricing_patterns", False):
            risk_score += 0.2
            flagged_reasons.append("Unusual pricing patterns detected")

        if analysis.get("high_dispute_rate", False):
            risk_score += 0.4
            flagged_reasons.append("High dispute rate detected")

        if analysis.get("suspicious_activity", False):
            risk_score += 0.3
            flagged_reasons.append("Suspicious activity patterns detected")

        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Generate AI-powered fraud analysis if AI is available
        ai_analysis = None
        try:
            from ..routers.ai import generate_ai_response, AI_SERVICE_ENABLED

            if AI_SERVICE_ENABLED:
                context = f"""
                User Fraud Analysis:
                - User ID: {user_id}
                - Risk Score: {risk_score}
                - Risk Level: {risk_level}
                - Flagged Reasons: {", ".join(flagged_reasons)}
                - Activity Analysis: {analysis}
                
                Provide detailed fraud analysis and recommendations for this user.
                """

                ai_analysis = generate_ai_response(
                    "Analyze this user's fraud risk and provide detailed insights:",
                    context,
                )
        except Exception as e:
            logger.warning(f"AI fraud analysis failed: {e}")

        # Create fraud report if risk is medium or high
        if risk_level in ["medium", "high"]:
            create_fraud_report(
                entity_type="user",
                entity_id=user_id,
                risk_score=risk_score,
                risk_level=risk_level,
                flagged_reasons=flagged_reasons,
                detection_method="pattern_analysis",
                confidence=0.8,
            )

        result = {
            "user_id": user_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "flagged_reasons": flagged_reasons,
            "analysis": analysis,
        }

        if ai_analysis:
            result["ai_analysis"] = ai_analysis

        return result

    except Exception as e:
        logger.error(f"Error checking user fraud: {e}")
        return {"error": f"Failed to analyze user: {str(e)}"}


def check_listing_fraud(listing_id: int) -> dict:
    """Check listing for fraud patterns"""
    try:
        # Analyze listing suspiciousness
        analysis = analyze_listing_patterns(listing_id)

        if "error" in analysis:
            return analysis

        # Calculate risk score
        risk_score = 0.0
        flagged_reasons = []

        # Check for suspicious patterns
        if analysis.get("suspicious_title", False):
            risk_score += 0.2
            flagged_reasons.append("Suspicious title detected")

        if analysis.get("unrealistic_pricing", False):
            risk_score += 0.3
            flagged_reasons.append("Unrealistic pricing detected")

        if analysis.get("duplicate_content", False):
            risk_score += 0.4
            flagged_reasons.append("Duplicate content detected")

        if analysis.get("spam_keywords", False):
            risk_score += 0.3
            flagged_reasons.append("Spam keywords detected")

        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Create fraud report if risk is medium or high
        if risk_level in ["medium", "high"]:
            create_fraud_report(
                entity_type="listing",
                entity_id=listing_id,
                risk_score=risk_score,
                risk_level=risk_level,
                flagged_reasons=flagged_reasons,
                detection_method="content_analysis",
                confidence=0.8,
            )

        return {
            "listing_id": listing_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "flagged_reasons": flagged_reasons,
            "analysis": analysis,
        }

    except Exception as e:
        logger.error(f"Error checking listing fraud: {e}")
        return {"error": f"Failed to analyze listing: {str(e)}"}


def check_payment_fraud(order_id: int) -> dict:
    """Check payment for fraud patterns"""
    try:
        # Analyze payment fraud
        analysis = detect_payment_fraud(order_id)

        if "error" in analysis:
            return analysis

        # Calculate risk score
        risk_score = 0.0
        flagged_reasons = []

        # Check for suspicious patterns
        if analysis.get("unusual_amount", False):
            risk_score += 0.3
            flagged_reasons.append("Unusual payment amount detected")

        if analysis.get("rapid_transactions", False):
            risk_score += 0.4
            flagged_reasons.append("Rapid transactions detected")

        if analysis.get("suspicious_timing", False):
            risk_score += 0.2
            flagged_reasons.append("Suspicious transaction timing")

        if analysis.get("pattern_anomaly", False):
            risk_score += 0.3
            flagged_reasons.append("Transaction pattern anomaly detected")

        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Create fraud report if risk is medium or high
        if risk_level in ["medium", "high"]:
            create_fraud_report(
                entity_type="payment",
                entity_id=order_id,
                risk_score=risk_score,
                risk_level=risk_level,
                flagged_reasons=flagged_reasons,
                detection_method="payment_analysis",
                confidence=0.8,
            )

        return {
            "order_id": order_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "flagged_reasons": flagged_reasons,
            "analysis": analysis,
        }

    except Exception as e:
        logger.error(f"Error checking payment fraud: {e}")
        return {"error": f"Failed to analyze payment: {str(e)}"}


@router.post("/check-user/{user_id}")
async def check_user_fraud_endpoint(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Check user for fraud patterns (admin only)"""
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can check for fraud",
        )

    result = check_user_fraud(user_id)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"],
        )

    return result


@router.post("/check-listing/{listing_id}")
async def check_listing_fraud_endpoint(
    listing_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Check listing for fraud patterns (admin only)"""
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can check for fraud",
        )

    result = check_listing_fraud(listing_id)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"],
        )

    return result


@router.post("/check-payment/{order_id}")
async def check_payment_fraud_endpoint(
    order_id: int,
    current_user: dict = Depends(get_current_active_user),
):
    """Check payment for fraud patterns (admin only)"""
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can check for fraud",
        )

    result = check_payment_fraud(order_id)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"],
        )

    return result


@router.get("/reports", response_model=FraudDetectionResponse)
async def get_fraud_reports(
    current_user: dict = Depends(get_current_active_user),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """Get fraud detection reports (admin only)"""
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view fraud reports",
        )

    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fraud detection service not available",
        )

    try:
        query = (
            supabase.table("fraud_reports").select("*").order("created_at", desc=True)
        )

        if risk_level:
            query = query.eq("risk_level", risk_level)
        if status_filter:
            query = query.eq("status", status_filter)

        # Calculate pagination
        skip = (page - 1) * page_size
        response = query.range(skip, skip + page_size - 1).execute()

        reports = response.data or []

        # Get summary statistics
        total_response = supabase.table("fraud_reports").select("id").execute()

        high_risk_response = (
            supabase.table("fraud_reports")
            .select("id")
            .eq("risk_level", "high")
            .execute()
        )

        medium_risk_response = (
            supabase.table("fraud_reports")
            .select("id")
            .eq("risk_level", "medium")
            .execute()
        )

        pending_response = (
            supabase.table("fraud_reports")
            .select("id")
            .eq("status", "pending")
            .execute()
        )

        summary = FraudDetectionSummary(
            total_reports=len(total_response.data) if total_response.data else 0,
            high_risk_reports=len(high_risk_response.data)
            if high_risk_response.data
            else 0,
            medium_risk_reports=len(medium_risk_response.data)
            if medium_risk_response.data
            else 0,
            pending_investigation=len(pending_response.data)
            if pending_response.data
            else 0,
            recent_activity=reports[:5],  # Top 5 recent reports
            risk_trends={
                "user_fraud": len(
                    [r for r in reports if r.get("entity_type") == "user"]
                ),
                "listing_fraud": len(
                    [r for r in reports if r.get("entity_type") == "listing"]
                ),
                "payment_fraud": len(
                    [r for r in reports if r.get("entity_type") == "payment"]
                ),
            },
        )

        return FraudDetectionResponse(
            reports=reports,
            summary=summary,
            total_count=len(total_response.data) if total_response.data else 0,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        logger.error(f"Error fetching fraud reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch fraud reports",
        )


@router.patch("/reports/{report_id}/status")
async def update_fraud_report_status(
    report_id: int,
    status: str,
    admin_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
):
    """Update fraud report status (admin only)"""
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update fraud reports",
        )

    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fraud detection service not available",
        )

    try:
        # Update report status
        update_data = {"status": status}
        if admin_notes:
            update_data["admin_notes"] = admin_notes

        response = (
            supabase.table("fraud_reports")
            .update(update_data)
            .eq("id", report_id)
            .execute()
        )

        if response.data:
            return {"message": f"Fraud report {report_id} status updated to {status}"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fraud report not found",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating fraud report status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update fraud report status",
        )


@router.post("/auto-scan")
async def trigger_auto_fraud_scan(
    current_user: dict = Depends(get_current_active_user),
):
    """Trigger automatic fraud scan (admin only)"""
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can trigger fraud scans",
        )

    try:
        # Get recent users to scan
        users_response = (
            supabase.table("users")
            .select("id")
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )

        # Get recent listings to scan
        listings_response = (
            supabase.table("listings")
            .select("id")
            .eq("is_active", True)
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )

        # Get recent orders to scan
        orders_response = (
            supabase.table("orders")
            .select("id")
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )

        scan_results = {
            "users_scanned": 0,
            "listings_scanned": 0,
            "orders_scanned": 0,
            "fraud_reports_created": 0,
        }

        # Scan users
        for user in users_response.data or []:
            result = check_user_fraud(user["id"])
            if "error" not in result and result.get("risk_level") in ["medium", "high"]:
                scan_results["fraud_reports_created"] += 1
            scan_results["users_scanned"] += 1

        # Scan listings
        for listing in listings_response.data or []:
            result = check_listing_fraud(listing["id"])
            if "error" not in result and result.get("risk_level") in ["medium", "high"]:
                scan_results["fraud_reports_created"] += 1
            scan_results["listings_scanned"] += 1

        # Scan orders
        for order in orders_response.data or []:
            result = check_payment_fraud(order["id"])
            if "error" not in result and result.get("risk_level") in ["medium", "high"]:
                scan_results["fraud_reports_created"] += 1
            scan_results["orders_scanned"] += 1

        return {
            "message": "Automatic fraud scan completed",
            "results": scan_results,
        }

    except Exception as e:
        logger.error(f"Error triggering fraud scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger fraud scan",
        )
