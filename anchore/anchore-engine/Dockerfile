FROM docker.io/anchore/anchore-engine:v0.3.4

COPY /anchore/anchore-engine/config/* /config/

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["anchore-manager", "service", "start", "--all"]
