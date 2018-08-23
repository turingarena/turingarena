from turingarena_impl.driver.interface.interface import InterfaceDefinition


def generate_interface_metadata(interface: InterfaceDefinition):
    return dict(
        constants=interface.constants,
        methods=[
            dict(
                name=method.name,
                has_return_value=method.has_return_value,
                parameters=[
                    dict(
                        name=parameter.name,
                        dimensions=parameter.dimensions,
                    )
                    for parameter in method.parameters
                ],
                callbacks=[
                    dict(
                        name=callback.name,
                        has_return_value=method.has_return_value,
                        parameters=[
                            dict(
                                name=parameter.name,
                                dimensions=parameter.dimensions,
                            )
                            for parameter in callback.parameters
                        ],
                    )
                    for callback in method.callbacks
                ],
            )
            for method in interface.methods
        ]
    )
