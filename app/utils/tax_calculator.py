# app/utils/tax_calculator.py
from typing import Dict, Tuple, List, Optional
from datetime import datetime

class IndianTaxCalculator:
    """
    Utility class for calculating Indian income tax based on the income tax slab rates.
    Implements tax calculation logic for different fiscal years and tax regimes.
    """
    
    def __init__(self, fiscal_year: str = None):
        """
        Initialize the tax calculator for a specific fiscal year.
        If no fiscal year is provided, the current fiscal year is used.
        """
        self.fiscal_year = fiscal_year or self._get_current_fiscal_year()
        
    @staticmethod
    def _get_current_fiscal_year() -> str:
        """
        Get the current fiscal year in the format "YYYY-YY".
        In India, the fiscal year runs from April 1 to March 31.
        """
        today = datetime.now()
        if today.month < 4:  # Jan to Mar
            return f"{today.year-1}-{str(today.year)[-2:]}"
        else:  # Apr to Dec
            return f"{today.year}-{str(today.year+1)[-2:]}"
    
    def calculate_tax(
        self, 
        income: float, 
        age: int = 35, 
        is_new_regime: bool = False,
        deductions: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        Calculate income tax based on the provided income, age, and tax regime.
        
        Args:
            income: Gross total income
            age: Age of the taxpayer
            is_new_regime: Whether to use the new tax regime (default: False)
            deductions: Dictionary of deductions with section codes as keys
            
        Returns:
            Dictionary with tax calculation details
        """
        deductions = deductions or {}
        
        if is_new_regime:
            # New regime doesn't consider most deductions
            taxable_income = income
            tax_liability = self._calculate_tax_new_regime(taxable_income, age)
        else:
            # Calculate taxable income after deductions
            total_deductions = sum(deductions.values())
            # Cap standard deductions at limits
            standard_deduction = min(50000, deductions.get("standard", 0))
            sec_80c = min(150000, deductions.get("80C", 0))
            sec_80d = min(25000, deductions.get("80D", 0))  # Basic limit
            
            # Apply age-based additional limits for 80D
            if age >= 60:
                sec_80d = min(50000, deductions.get("80D", 0))
                
            # Calculate other deductions
            hra_exemption = deductions.get("HRA", 0)
            home_loan_interest = min(200000, deductions.get("24B", 0))
            nps_contribution = min(50000, deductions.get("80CCD(1B)", 0))
            
            # Calculate total eligible deductions
            eligible_deductions = (
                standard_deduction + 
                sec_80c + 
                sec_80d + 
                hra_exemption + 
                home_loan_interest + 
                nps_contribution
            )
            
            # Calculate taxable income
            taxable_income = max(0, income - eligible_deductions)
            
            # Calculate tax liability based on old regime
            tax_liability = self._calculate_tax_old_regime(taxable_income, age)
        
        # Calculate education cess (4%)
        education_cess = tax_liability * 0.04
        
        # Calculate total tax liability
        total_tax_liability = tax_liability + education_cess
        
        return {
            "gross_income": income,
            "total_deductions": sum(deductions.values()),
            "eligible_deductions": eligible_deductions if not is_new_regime else 0,
            "taxable_income": taxable_income,
            "tax_liability": tax_liability,
            "education_cess": education_cess,
            "total_tax_liability": total_tax_liability
        }
    
    def _calculate_tax_old_regime(self, taxable_income: float, age: int) -> float:
        """
        Calculate tax under the old regime based on income slabs and age.
        """
        # Define tax slabs based on age (for 2023-24)
        if age >= 80:  # Super senior citizen
            slabs = [
                (0, 500000, 0),
                (500000, 1000000, 0.20),
                (1000000, float('inf'), 0.30)
            ]
        elif age >= 60:  # Senior citizen
            slabs = [
                (0, 300000, 0),
                (300000, 500000, 0.05),
                (500000, 1000000, 0.20),
                (1000000, float('inf'), 0.30)
            ]
        else:  # Others
            slabs = [
                (0, 250000, 0),
                (250000, 500000, 0.05),
                (500000, 1000000, 0.20),
                (1000000, float('inf'), 0.30)
            ]
        
        # Apply tax rebate if applicable (Section 87A)
        if taxable_income <= 500000:
            rebate = min(12500, taxable_income)
        else:
            rebate = 0
        
        # Calculate tax based on slabs
        tax = 0
        for lower, upper, rate in slabs:
            if taxable_income > lower:
                slab_income = min(taxable_income, upper) - lower
                tax += slab_income * rate
        
        # Apply rebate
        tax = max(0, tax - rebate)
        
        return tax
    
    def _calculate_tax_new_regime(self, taxable_income: float, age: int) -> float:
        """
        Calculate tax under the new regime based on income slabs.
        Age doesn't affect tax slabs in the new regime.
        """
        # New regime slabs for 2023-24
        slabs = [
            (0, 250000, 0),
            (250000, 500000, 0.05),
            (500000, 750000, 0.10),
            (750000, 1000000, 0.15),
            (1000000, 1250000, 0.20),
            (1250000, 1500000, 0.25),
            (1500000, float('inf'), 0.30)
        ]
        
        # Apply tax rebate if applicable (Section 87A)
        if taxable_income <= 700000:  # Increased to 7 lakhs in new regime
            rebate = min(25000, taxable_income)
        else:
            rebate = 0
        
        # Calculate tax based on slabs
        tax = 0
        for lower, upper, rate in slabs:
            if taxable_income > lower:
                slab_income = min(taxable_income, upper) - lower
                tax += slab_income * rate
        
        # Apply rebate
        tax = max(0, tax - rebate)
        
        return tax
    
    def determine_itr_form(
        self,
        income_sources: List[str],
        has_capital_gains: bool = False,
        has_foreign_income: bool = False,
        has_business_income: bool = False
    ) -> str:
        """
        Determine which ITR form is appropriate based on income sources.
        
        Args:
            income_sources: List of income sources
            has_capital_gains: Whether taxpayer has capital gains
            has_foreign_income: Whether taxpayer has foreign income
            has_business_income: Whether taxpayer has business or profession income
            
        Returns:
            Appropriate ITR form (ITR-1, ITR-2, etc.)
        """
        # ITR-1 (Sahaj): For individuals with income only from salary, one house property, 
        # other sources (excluding lottery, gambling, etc.)
        if (len(income_sources) <= 3 and 
            all(source in ['salary', 'house_property', 'other_sources'] for source in income_sources) and
            not has_capital_gains and 
            not has_foreign_income and 
            not has_business_income):
            return "ITR-1"
        
        # ITR-2: For individuals and HUFs with income from salary, house property, 
        # capital gains, and other sources
        elif not has_business_income:
            return "ITR-2"
        
        # ITR-3: For individuals and HUFs having income from business or profession
        elif has_business_income:
            return "ITR-3"
        
        # ITR-4 (Sugam): For presumptive income from business or profession
        elif has_business_income and any(source == 'presumptive_income' for source in income_sources):
            return "ITR-4"
        
        # Default to ITR-2 if no clear determination
        else:
            return "ITR-2"
    
    def get_tax_saving_suggestions(self, current_deductions: Dict[str, float]) -> List[Dict[str, any]]:
        """
        Provide tax saving suggestions based on unused deduction limits.
        
        Args:
            current_deductions: Dictionary of current deductions with section codes as keys
            
        Returns:
            List of tax saving suggestions
        """
        suggestions = []
        
        # 80C suggestions
        current_80c = current_deductions.get("80C", 0)
        if current_80c < 150000:
            remaining_80c = 150000 - current_80c
            suggestions.append({
                "section": "80C",
                "description": "Tax deduction on investments like PPF, ELSS, NSC, etc.",
                "current_amount": current_80c,
                "max_limit": 150000,
                "remaining_limit": remaining_80c,
                "recommendations": [
                    {"name": "ELSS Mutual Funds", "description": "Equity Linked Savings Scheme with 3-year lock-in"},
                    {"name": "PPF", "description": "Public Provident Fund with 15-year lock-in"},
                    {"name": "NPS Tier-1", "description": "National Pension System contribution"},
                    {"name": "Tax Saving FD", "description": "5-year tax-saving fixed deposits"}
                ]
            })
        
        # 80D suggestions
        current_80d = current_deductions.get("80D", 0)
        if current_80d < 25000:  # Assuming under 60 years
            remaining_80d = 25000 - current_80d
            suggestions.append({
                "section": "80D",
                "description": "Health Insurance Premium",
                "current_amount": current_80d,
                "max_limit": 25000,
                "remaining_limit": remaining_80d,
                "recommendations": [
                    {"name": "Health Insurance", "description": "Medical insurance for self and family"},
                    {"name": "Preventive Health Check-up", "description": "Up to ₹5,000 within the overall limit"}
                ]
            })
        
        # 80CCD(1B) suggestions - Additional NPS
        current_nps = current_deductions.get("80CCD(1B)", 0)
        if current_nps < 50000:
            remaining_nps = 50000 - current_nps
            suggestions.append({
                "section": "80CCD(1B)",
                "description": "Additional deduction for NPS contribution",
                "current_amount": current_nps,
                "max_limit": 50000,
                "remaining_limit": remaining_nps,
                "recommendations": [
                    {"name": "NPS Tier-1", "description": "Additional contribution to National Pension System"}
                ]
            })
        
        # Home Loan Interest suggestions
        current_home_loan = current_deductions.get("24B", 0)
        if current_home_loan < 200000:
            remaining_home_loan = 200000 - current_home_loan
            suggestions.append({
                "section": "24B",
                "description": "Interest on Housing Loan",
                "current_amount": current_home_loan,
                "max_limit": 200000,
                "remaining_limit": remaining_home_loan,
                "recommendations": [
                    {"name": "Home Loan", "description": "Interest paid on housing loan for self-occupied property"}
                ]
            })
        
        # 80E suggestions - Education Loan
        if "80E" not in current_deductions or current_deductions.get("80E", 0) == 0:
            suggestions.append({
                "section": "80E",
                "description": "Interest on Education Loan",
                "current_amount": 0,
                "max_limit": "No upper limit",
                "remaining_limit": "Full amount eligible",
                "recommendations": [
                    {"name": "Education Loan Interest", "description": "Interest paid on loan taken for higher education"}
                ]
            })
        
        return suggestions
    
    def compare_tax_regimes(
        self, 
        income: float, 
        age: int, 
        deductions: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Compare tax liability under old and new tax regimes.
        
        Args:
            income: Gross total income
            age: Age of the taxpayer
            deductions: Dictionary of deductions with section codes as keys
            
        Returns:
            Comparison of tax under both regimes
        """
        old_regime_tax = self.calculate_tax(income, age, False, deductions)
        new_regime_tax = self.calculate_tax(income, age, True, deductions)
        
        savings = old_regime_tax["total_tax_liability"] - new_regime_tax["total_tax_liability"]
        better_regime = "new" if savings > 0 else "old"
        
        return {
            "old_regime": old_regime_tax,
            "new_regime": new_regime_tax,
            "difference": abs(savings),
            "better_regime": better_regime,
            "savings": max(0, savings)
        }