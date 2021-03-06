# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging

from . import imcgenutils
from . import imccoreutils
from .imcexception import ImcException
from .imcconstants import NamingId
from .imcsession import ImcSession

log = logging.getLogger('imc')


class ImcHandle(ImcSession):
    """
    ImcHandle class is the user interface point for any Imc communication.

    Args:
        ip (str): The IP or Hostname of the IMC Server
        username (str): The username as configured on the Imc Server
        password (str): The password as configured on the Imc Server
        port (int or None): The port number to be used during connection
        secure (bool or None): True for secure connection, otherwise False
        proxy (str): The proxy object to be used to connect

    Example:
        handle = ImcHandle("192.168.1.1","admin","password")\n
        handle = ImcHandle("192.168.1.1","admin","password", secure=True)\n
        handle = ImcHandle("192.168.1.1","admin","password", secure=False)\n
        handle = ImcHandle("192.168.1.1","admin","password", port=80)\n
        handle = ImcHandle("192.168.1.1","admin","password", port=443)\n
        handle = ImcHandle("192.168.1.1","admin","password", port=100,
                 secure=True)\n
        handle = ImcHandle("192.168.1.1","admin","password", port=100,
                 secure=False)\n
    """

    def __init__(self, ip, username, password, port=None, secure=None,
                 proxy=None):
        ImcSession.__init__(self, ip, username, password, port, secure, proxy)
        self.__to_commit = {}

    def set_dump_xml(self):
        """
        Enables the logging of xml requests and responses.
        """

        self._set_dump_xml()

    def unset_dump_xml(self):
        """
        Disables the logging of xml requests and responses.
        """

        self._unset_dump_xml()

    def login(self, auto_refresh=False, force=False):
        """
        Initiates a connection to the server referenced by the ImcHandle.
        A cookie is populated in the ImcHandle, if the login is successful.

        Args:
            auto_refresh (bool): if set to True, it refresh the cookie
                continuously
            force (bool): if set to True it reconnects even if cookie exists
                and is valid for respective connection.

        Returns:
            True on successful connect

        Example:
            handle.login()\n
            handle.login(auto_refresh=True)\n
            handle.login(force=True)\n
            handle.login(auto_refresh=True, force=True)\n

            where handle is ImcHandle()
        """

        return self._login(auto_refresh, force)

    def logout(self):
        """
        Disconnects from the server referenced by the ImcHandle.

        Args:
            None

        Returns:
            True on successful disconnect

        Example:
            handle.logout()

            where handle is ImcHandle()
        """

        return self._logout()

    def process_xml_elem(self, elem):
        """
        process_xml_elem is a helper method which posts xml elements to the
        server and returns parsed response. It's role is to operate on the
        output of methods from Imcmethodfactory, which return xml element
        node(s).

        Args:
            elem (xml element object)

        Returns:
            mo list or external method object

        Example:
            elem = imcmethodfactory.config_find_dns_by_class_id(cookie=
                handle.cookie, class_id="LsServer", in_filter=None)\n
            dn_objs = handle.process_xml_elem(elem)
        """

        response = self.post_elem(elem)
        if response.error_code != 0:
            raise ImcException(response.error_code, response.error_descr)

        if hasattr(response, "out_config"):
            return response.out_config.child
        else:
            return response

    def get_auth_token(self):
        """
        Returns a token that is used for IMC authentication.

        Args:
            None

        Returns:
            auth_token (str)

        Example:
            handle.get_auth_token()

        """

        from .imcmethodfactory import aaa_get_compute_auth_tokens

        auth_token = None
        mo = self.query_classid(class_id=NamingId.COMPUTE_BOARD)
        if not mo:
            mo = self.query_classid(class_id=NamingId.COMPUTE_RACK_UNIT)

        if mo:
            elem = aaa_get_compute_auth_tokens(cookie=self.cookie)
            response = self.post_elem(elem)
            if response.error_code != 0:
                raise ImcException(response.error_code,
                                   response.error_descr)

            # cat = self.AaaGetNComputeAuthTokenByDn(mo[0].Dn, 1, None)
            auth_token = response.out_tokens.split(',')[0]

        return auth_token

    def query_dn(self, dn, hierarchy=False, need_response=False):
        """
        Finds an object using it's distinguished name.

        Args:
            dn (str): distinguished name of the object to be queried for.
            hierarchy(bool): True/False,
                                get all objects in hierarchy if True
            need_response(bool): True/False,
                                return the response xml node, instead of parsed
                                objects

        Returns:
            managedobject or None   by default\n
            managedobject list      if hierarchy=True\n
            externalmethod object   if need_response=True\n

        Example:
            obj = handle.lookup_by_dn("fabric/lan/net-100")\n
            obj = handle.lookup_by_dn("fabric/lan/net-100", hierarchy=True)\n
            obj = handle.lookup_by_dn("fabric/lan/net-100", need_response=True)\n
            obj = handle.lookup_by_dn("fabric/lan/net-100", hierarchy=True, need_response=True)\n
        """

        from .imcmethodfactory import config_resolve_dn

        if not dn:
            raise ValueError("Provide dn.")

        elem = config_resolve_dn(cookie=self.cookie,dn=dn,
                                 in_hierarchical=hierarchy)
        response = self.post_elem(elem)
        if response.error_code != 0:
            raise ImcException(response.error_code, response.error_descr)

        if need_response:
            return response

        if hierarchy:
            out_mo_list = imccoreutils.extract_molist_from_method_response(
                response,
                hierarchy)
            return out_mo_list

        mo = None
        if len(response.out_config.child) > 0:
            mo = response.out_config.child[0]
        return mo

    def query_classid(self, class_id=None, hierarchy=False,
                      need_response=False):
        """
        Finds an object using it's class id.

        Args:
            class_id (str): class id of the object to be queried for.

            hierarchy(bool): if set to True will return all the child
                             hierarchical objects.
            need_response(bool): if set to True will return only response
                                object.


        Returns:
            managedobjectlist or None   by default\n
            managedobjectlist or None   if hierarchy=True\n
            methodresponse              if need_response=True\n

        Example:
            obj = handle.query_classid(class_id="LsServer")\n
            obj = handle.query_classid(class_id="LsServer", hierarchy=True)\n
            obj = handle.query_classid(class_id="LsServer", need_response=True)\n

        """

        # ToDo - How to handle unknown class_id

        from .imcmethodfactory import config_resolve_class

        if not class_id:
            raise ValueError("Provide Parameter class_id")

        meta_class_id = imccoreutils.find_class_id_in_mo_meta_ignore_case(
                                                                class_id)
        if not meta_class_id:
            meta_class_id = class_id
        elem = config_resolve_class(cookie=self.cookie,
                                    class_id=meta_class_id,
                                    in_hierarchical=hierarchy)
        response = self.post_elem(elem)
        if response.error_code != 0:
            raise ImcException(response.error_code, response.error_descr)

        if need_response:
            return response

        out_mo_list = imccoreutils.extract_molist_from_method_response(
                                                                    response,
                                                                    hierarchy)
        return out_mo_list

    def query_children(self, in_mo=None, in_dn=None, class_id=None,
                       hierarchy=False):
        """
        Finds children of a given managed object or distinguished name.
        Arguments can be specified to query only a specific type(class_id)
        of children.
        Arguments can also be specified to query only direct children or the
        entire hierarchy of children.

        Args:
            in_mo (managed object): query children managed object under this
                                        object.
            in_dn (dn string): query children managed object for a
                                given managed object of the respective dn.
            class_id(str): by default None, if given find only specific
                            children object for a given class_id.
            hierarchy(bool): if set to True will return all the child
                              hierarchical objects.

        Returns:
            managedobjectlist or None   by default\n
            managedobjectlist or None   if hierarchy=True\n

        Example:
            mo_list = handle.query_children(in_mo=mo)\n
            mo_list = handle.query_children(in_mo=mo, class_id="classid")\n
            mo_list = handle.query_children(in_dn=dn)\n
            mo_list = handle.query_children(in_dn=dn, class_id="classid")\n
        """

        from .imcmethodfactory import config_resolve_children

        if not in_mo and not in_dn:
            raise ValueError('[Error]: GetChild: Provide in_mo or in_dn.')

        if in_mo:
            parent_dn = in_mo.dn
        elif in_dn:
            parent_dn = in_dn

        if class_id:
            meta_class_id = imccoreutils.find_class_id_in_mo_meta_ignore_case(
                class_id)
            if not meta_class_id:
                meta_class_id = class_id
        else:
            meta_class_id = class_id

        elem = config_resolve_children(cookie=self.cookie,
                                       class_id=meta_class_id,
                                       in_dn=parent_dn,
                                       in_hierarchical=hierarchy)

        response = self.post_elem(elem)
        if response.error_code != 0:
            raise ImcException(response.error_code, response.error_descr)

        out_mo_list = imccoreutils.extract_molist_from_method_response(response,
                                                                       hierarchy
                                                                       )

        return out_mo_list

    def add_mo(self, mo, modify_present=False):
        """
        Adds a managed object to the ImcHandle commit buffer.
        This method does not trigger a commit by itself.
        This needs to be followed by a handle.commit() either immediately or
        after more operations to ensure successful addition of object on server

        Args:
            mo (managedobject): ManagedObject to be added.
            modify_present (bool): True/False,
                                    overwrite existing object if True

        Returns:
            None

        Example:
            obj = handle.add_mo(mo)
        """

        if modify_present in imcgenutils.AFFIRMATIVE_LIST:
            mo.status = "modified"
        else:
            mo.status = "created"

        self.__to_commit[mo.dn] = mo
        self._commit()

    def set_mo(self, mo):
        """
        Modifies a managed object and adds it to ImcHandle commit buffer (if
         not already in it).
        This method does not trigger a commit by itself.
        This needs to be followed by a handle.commit() either immediately or
        after more operations to ensure successful modification of object on
        server.

        Args:
            mo (managedobject): Managed object with modified properties.

        Returns:
            None

        Example:
            obj = handle.set_mo(mo)
        """

        mo.status = "modified"
        self.__to_commit[mo.dn] = mo
        self._commit()

    def remove_mo(self, mo):
        """
        Removes a managed object.
        This method does not trigger a commit by itself.
        This needs to be followed by a handle.commit() either immediately or
        after more operations to ensure successful removal of object from the
        server.

        Args:
            mo (managedobject): Managed object to be removed.

        Returns:
            None

        Example:
            obj = handle.remove_mo(mo)
        """

        mo.status = "deleted"
        if mo.parent_mo:
            mo.parent_mo.child_remove(mo)

        self.__to_commit[mo.dn] = mo
        self._commit()

    def _commit(self):
        """
        Commit the buffer to the server. Pushes all the configuration changes
        so far to the server.
        Configuration could be added to the commit buffer using add_mo(),
        set_mo(), remove_mo() prior to making a handle.commit()

        Args:
            None

        Returns:
            None

        Example:
            self._commit()
        """

        from .imcbasetype import ConfigMap
        from .imcmethodfactory import config_conf_mo
        mo_dict = self.__to_commit
        if not mo_dict:
            log.debug("Commit Buffer is Empty")
            return None

        config_map = ConfigMap()
        for mo_dn in mo_dict:
        
            config_map.child_add(mo_dict[mo_dn])
            elem = config_conf_mo(self.cookie,dn=mo_dn,
                                  in_config=config_map,
                                  in_hierarchical=False)
            response = self.post_elem(elem)
            if response.error_code != 0:
                raise ImcException(response.error_code, response.error_descr)

            for pair_ in response.out_config.child:
                for out_mo in pair_.child:
                    out_mo.sync_mo(mo_dict[out_mo.dn])

        self.__to_commit = {}
