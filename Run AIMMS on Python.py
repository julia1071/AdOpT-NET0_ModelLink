import subprocess

# Define the AIMMS executable and the model path
command = (
    '"C:\\Program Files\\Aimms-25.4.1.2-x64-VS2022.exe" ' #The location of the AIMMS program
    '"U:\\IESA-Opt_latestversion\\20250429_IESA Slack - detailed.aimms" ' #The location of AIMMS project IESA-Opt
    '--run-only "Linking_Procedure" ' # Here, chronologically the procedures can be started.
    '--run-only "InitiliazeRESTServer" --end-user'
)
# Run the command
ret = subprocess.call(command, shell=True)