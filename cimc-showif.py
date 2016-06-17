from ImcSdk import *
handle = ImcHandle()
handle.login("10.82.79.42", username="admin", password="cisco")
handle.get_imc_managedobject(None, 'adaptorExtEthIf', params=None,in_hierarchical=False,dump_xml='yes')
handle.logout()

