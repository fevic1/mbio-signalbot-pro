from .manifest import RuntimeManifest


class ManifestLoader:

    def load(self, data: dict) -> RuntimeManifest:
        return RuntimeManifest(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            services=list(data.get("services", [])),
            plugins=list(data.get("plugins", [])),
            extensions=list(data.get("extensions", [])),
            metadata=dict(data.get("metadata", {})),
        )

    def dump(self, manifest: RuntimeManifest) -> dict:
        return {
            "name": manifest.name,
            "version": manifest.version,
            "services": list(manifest.services),
            "plugins": list(manifest.plugins),
            "extensions": list(manifest.extensions),
            "metadata": dict(manifest.metadata),
        }
