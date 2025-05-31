from classifier_agent import ClassifierAgent
from json_agent import JSONAgent
from pdf_agent import PDFAgent
from shared_memory import SharedMemory

def main():
    memory = SharedMemory()
    classifier = ClassifierAgent()
    json_agent = JSONAgent(memory)
    pdf_agent = PDFAgent(classifier, json_agent, memory)

    sample_pdf_path = r"D:\sample_invoice.pdf"  # <-- your PDF path here

    result = pdf_agent.process_pdf(sample_pdf_path)

    print("\nFinal Routed Result:\n", result)
    print("\nFull Memory Log:\n", memory.get_all())

if __name__ == "__main__":
    main()
