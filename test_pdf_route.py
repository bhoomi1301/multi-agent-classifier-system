from agent_orchestrator import AgentOrchestrator

# Path to your test PDF file
pdf_file_path = r"D:\sample_invoice.pdf"  # Make sure this file exists

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Call the route_input method with the PDF file path
result = orchestrator.route_input(pdf_file_path)

# Print the result
print("\n=== PDF Processing Result ===")
print(result)
