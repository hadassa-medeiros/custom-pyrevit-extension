class Convert:
    @staticmethod
    def m_to_ft(metros):
        return round(metros * 3.28084, 5)
    
    @staticmethod
    def ft_to_m(pes):
        return round(pes / 3.28084, 5)

def cleanup_str(str):
    return cleanup_str.strip.upper()
    