def get_docs(df):
    """
    Converts a DataFrame of lab info into a list of dictionaries with 'index' and 'text' keys.
    """
    docs = []

    for _, row in df.iterrows():
        try:
            lab_info = {
                "index": row.get("index", "Unknown"),
                "research_institute": row.get("research_institute", "Unknown"),
                "department": row.get("department", "Unknown"),
                "lab_name": row.get("lab_name", "Unknown"),
                "research_keywords": row.get("research_keywords", "Unknown"),
                "research_topics": row.get("research_topics", "Unknown"),
                "research_techniques": row.get("research_techniques", "Unknown"),
                "lab_description": row.get("lab_description", "Unknown"),
            }

            lab_search_docs = {
                "index": lab_info["index"],
                "text": f"Research Institute: {lab_info['research_institute']}\n"
                        f"Department: {lab_info['department']}\n"
                        f"Lab Name: {lab_info['lab_name']}\n"
                        f"Research Keywords: {lab_info['research_keywords']}\n"
                        f"Research Topics: {lab_info['research_topics']}\n"
                        f"Research Techniques: {lab_info['research_techniques']}\n"
                        f"Lab Description: {lab_info['lab_description']}\n"
            }

            docs.append(lab_search_docs)

        except Exception as e:
            print(f"Error processing row: {e}")
            continue

    return docs
