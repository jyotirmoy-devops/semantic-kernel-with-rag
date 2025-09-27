from typing import List

def chunk_text(text: str, chunk_size: int = 100000, overlap: int = 1000) -> List[str]:
    """
    Split text into chunks with a specified overlap.
    
    Args:
        text (str): The input text to be chunked
        chunk_size (int): Maximum size of each chunk in characters
        overlap (int): Number of characters to overlap between chunks
    
    Returns:
        List[str]: List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # If this is the last chunk, just take the rest of the text
        if start + chunk_size >= len(text):
            chunks.append(text[start:])
            break
            
        # Find the last period or space in the chunk to avoid cutting mid-sentence
        end = start + chunk_size
        last_period = text.rfind('.', start, end)
        last_space = text.rfind(' ', start, end)
        
        # Prefer splitting at periods, fall back to spaces
        split_point = last_period if last_period != -1 else last_space
        
        # If no good split point found, just split at chunk_size
        if split_point == -1 or split_point <= start:
            split_point = end
            
        chunks.append(text[start:split_point])
        
        # Move start point back by overlap amount
        start = split_point - overlap
        if start < 0:
            start = 0
            
    return chunks