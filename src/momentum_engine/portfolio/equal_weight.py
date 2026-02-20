class EqualWeightPortfolio:
    """
    Select top N stocks and assign equal weights.
    """

    @staticmethod
    def construct(ranked: list[str], top_n: int) -> dict[str, float]:
        selected = ranked[:top_n]
        weight = round(1 / top_n, 6)
        return {ticker: weight for ticker in selected}