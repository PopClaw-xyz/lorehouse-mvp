import * as $protobuf from "protobufjs";
import Long = require("long");
/** Namespace popclaw. */
export namespace popclaw {

    /** Namespace identity. */
    namespace identity {

        /** Role enum. */
        enum Role {
            RANGER = 0,
            HOST = 1
        }

        /** Properties of an ActorInfo. */
        interface IActorInfo {

            /** ActorInfo popclawId */
            popclawId?: (string|null);

            /** ActorInfo nickname */
            nickname?: (string|null);

            /** ActorInfo supersedes */
            supersedes?: (string|null);

            /** ActorInfo deviceId */
            deviceId?: (Uint8Array|null);

            /** ActorInfo role */
            role?: (popclaw.identity.Role|null);
        }

        /** Represents an ActorInfo. */
        class ActorInfo implements IActorInfo {

            /**
             * Constructs a new ActorInfo.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.identity.IActorInfo);

            /** ActorInfo popclawId. */
            public popclawId: string;

            /** ActorInfo nickname. */
            public nickname: string;

            /** ActorInfo supersedes. */
            public supersedes?: (string|null);

            /** ActorInfo deviceId. */
            public deviceId?: (Uint8Array|null);

            /** ActorInfo role. */
            public role?: (popclaw.identity.Role|null);

            /** ActorInfo _supersedes. */
            public _supersedes?: "supersedes";

            /** ActorInfo _deviceId. */
            public _deviceId?: "deviceId";

            /** ActorInfo _role. */
            public _role?: "role";

            /**
             * Creates a new ActorInfo instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ActorInfo instance
             */
            public static create(properties?: popclaw.identity.IActorInfo): popclaw.identity.ActorInfo;

            /**
             * Encodes the specified ActorInfo message. Does not implicitly {@link popclaw.identity.ActorInfo.verify|verify} messages.
             * @param message ActorInfo message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.identity.IActorInfo, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an ActorInfo message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ActorInfo
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.identity.ActorInfo;

            /**
             * Creates an ActorInfo message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ActorInfo
             */
            public static fromObject(object: { [k: string]: any }): popclaw.identity.ActorInfo;

            /**
             * Creates a plain object from an ActorInfo message. Also converts values to other types if specified.
             * @param message ActorInfo
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.identity.ActorInfo, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ActorInfo to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ActorInfo
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SignedPayload. */
        interface ISignedPayload {

            /** SignedPayload payload */
            payload?: (Uint8Array|null);

            /** SignedPayload signature */
            signature?: (Uint8Array|null);

            /** SignedPayload signerPubkey */
            signerPubkey?: (Uint8Array|null);
        }

        /** Represents a SignedPayload. */
        class SignedPayload implements ISignedPayload {

            /**
             * Constructs a new SignedPayload.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.identity.ISignedPayload);

            /** SignedPayload payload. */
            public payload: Uint8Array;

            /** SignedPayload signature. */
            public signature: Uint8Array;

            /** SignedPayload signerPubkey. */
            public signerPubkey: Uint8Array;

            /**
             * Creates a new SignedPayload instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SignedPayload instance
             */
            public static create(properties?: popclaw.identity.ISignedPayload): popclaw.identity.SignedPayload;

            /**
             * Encodes the specified SignedPayload message. Does not implicitly {@link popclaw.identity.SignedPayload.verify|verify} messages.
             * @param message SignedPayload message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.identity.ISignedPayload, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SignedPayload message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SignedPayload
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.identity.SignedPayload;

            /**
             * Creates a SignedPayload message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SignedPayload
             */
            public static fromObject(object: { [k: string]: any }): popclaw.identity.SignedPayload;

            /**
             * Creates a plain object from a SignedPayload message. Also converts values to other types if specified.
             * @param message SignedPayload
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.identity.SignedPayload, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SignedPayload to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SignedPayload
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }
    }

    /** Namespace event. */
    namespace event {

        /** Properties of a Recipient. */
        interface IRecipient {

            /** Recipient scope */
            scope?: (popclaw.event.Recipient.Scope|null);

            /** Recipient targetIds */
            targetIds?: (string[]|null);

            /** Recipient filterCriteria */
            filterCriteria?: (string|null);
        }

        /** Represents a Recipient. */
        class Recipient implements IRecipient {

            /**
             * Constructs a new Recipient.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IRecipient);

            /** Recipient scope. */
            public scope: popclaw.event.Recipient.Scope;

            /** Recipient targetIds. */
            public targetIds: string[];

            /** Recipient filterCriteria. */
            public filterCriteria: string;

            /**
             * Creates a new Recipient instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Recipient instance
             */
            public static create(properties?: popclaw.event.IRecipient): popclaw.event.Recipient;

            /**
             * Encodes the specified Recipient message. Does not implicitly {@link popclaw.event.Recipient.verify|verify} messages.
             * @param message Recipient message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IRecipient, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Recipient message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns Recipient
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.Recipient;

            /**
             * Creates a Recipient message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Recipient
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.Recipient;

            /**
             * Creates a plain object from a Recipient message. Also converts values to other types if specified.
             * @param message Recipient
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.Recipient, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Recipient to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for Recipient
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        namespace Recipient {

            /** Scope enum. */
            enum Scope {
                BROADCAST = 0,
                PRIVATE = 1,
                GROUP = 2,
                CONDITIONAL = 3
            }
        }

        /** Properties of an EventEnvelope. */
        interface IEventEnvelope {

            /** EventEnvelope eventId */
            eventId?: (string|null);

            /** EventEnvelope actor */
            actor?: (popclaw.identity.IActorInfo|null);

            /** EventEnvelope target */
            target?: (popclaw.event.IRecipient|null);

            /** EventEnvelope lorehouse */
            lorehouse?: (string|null);

            /** EventEnvelope timestamp */
            timestamp?: (number|Long|null);

            /** EventEnvelope signature */
            signature?: (Uint8Array|null);

            /** EventEnvelope prevEventId */
            prevEventId?: (string|null);

            /** EventEnvelope inviteRequest */
            inviteRequest?: (popclaw.invite.IInviteRequest|null);

            /** EventEnvelope questDispatch */
            questDispatch?: (popclaw.quest.IQuestDispatch|null);

            /** EventEnvelope questResult */
            questResult?: (popclaw.quest.IQuestResult|null);

            /** EventEnvelope inviteVerified */
            inviteVerified?: (popclaw.invite.IInviteVerified|null);

            /** EventEnvelope rangerRegistration */
            rangerRegistration?: (popclaw.event.IRangerRegistration|null);

            /** EventEnvelope watchDispatch */
            watchDispatch?: (popclaw.event.IWatchDispatch|null);

            /** EventEnvelope watchHeartbeat */
            watchHeartbeat?: (popclaw.event.IWatchHeartbeat|null);

            /** EventEnvelope watchCancel */
            watchCancel?: (popclaw.event.IWatchCancel|null);

            /** EventEnvelope followDeclared */
            followDeclared?: (popclaw.event.IFollowDeclared|null);

            /** EventEnvelope followRevoked */
            followRevoked?: (popclaw.event.IFollowRevoked|null);

            /** EventEnvelope reply */
            reply?: (popclaw.event.IReply|null);

            /** EventEnvelope directMessage */
            directMessage?: (popclaw.event.IDirectMessage|null);

            /** EventEnvelope post */
            post?: (popclaw.event.IPost|null);

            /** EventEnvelope profile */
            profile?: (popclaw.profile.IProfile|null);

            /** EventEnvelope mark */
            mark?: (popclaw.event.IMark|null);

            /** EventEnvelope markRevoked */
            markRevoked?: (popclaw.event.IMarkRevoked|null);

            /** EventEnvelope pollDispatch */
            pollDispatch?: (popclaw.event.IPollDispatch|null);

            /** EventEnvelope pollReport */
            pollReport?: (popclaw.event.IPollReport|null);

            /** EventEnvelope houseEvent */
            houseEvent?: (popclaw.event.IHouseEvent|null);

            /** EventEnvelope intent */
            intent?: (popclaw.event.IIntentPayload|null);
        }

        /** Represents an EventEnvelope. */
        class EventEnvelope implements IEventEnvelope {

            /**
             * Constructs a new EventEnvelope.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IEventEnvelope);

            /** EventEnvelope eventId. */
            public eventId: string;

            /** EventEnvelope actor. */
            public actor?: (popclaw.identity.IActorInfo|null);

            /** EventEnvelope target. */
            public target?: (popclaw.event.IRecipient|null);

            /** EventEnvelope lorehouse. */
            public lorehouse: string;

            /** EventEnvelope timestamp. */
            public timestamp: (number|Long);

            /** EventEnvelope signature. */
            public signature: Uint8Array;

            /** EventEnvelope prevEventId. */
            public prevEventId: string;

            /** EventEnvelope inviteRequest. */
            public inviteRequest?: (popclaw.invite.IInviteRequest|null);

            /** EventEnvelope questDispatch. */
            public questDispatch?: (popclaw.quest.IQuestDispatch|null);

            /** EventEnvelope questResult. */
            public questResult?: (popclaw.quest.IQuestResult|null);

            /** EventEnvelope inviteVerified. */
            public inviteVerified?: (popclaw.invite.IInviteVerified|null);

            /** EventEnvelope rangerRegistration. */
            public rangerRegistration?: (popclaw.event.IRangerRegistration|null);

            /** EventEnvelope watchDispatch. */
            public watchDispatch?: (popclaw.event.IWatchDispatch|null);

            /** EventEnvelope watchHeartbeat. */
            public watchHeartbeat?: (popclaw.event.IWatchHeartbeat|null);

            /** EventEnvelope watchCancel. */
            public watchCancel?: (popclaw.event.IWatchCancel|null);

            /** EventEnvelope followDeclared. */
            public followDeclared?: (popclaw.event.IFollowDeclared|null);

            /** EventEnvelope followRevoked. */
            public followRevoked?: (popclaw.event.IFollowRevoked|null);

            /** EventEnvelope reply. */
            public reply?: (popclaw.event.IReply|null);

            /** EventEnvelope directMessage. */
            public directMessage?: (popclaw.event.IDirectMessage|null);

            /** EventEnvelope post. */
            public post?: (popclaw.event.IPost|null);

            /** EventEnvelope profile. */
            public profile?: (popclaw.profile.IProfile|null);

            /** EventEnvelope mark. */
            public mark?: (popclaw.event.IMark|null);

            /** EventEnvelope markRevoked. */
            public markRevoked?: (popclaw.event.IMarkRevoked|null);

            /** EventEnvelope pollDispatch. */
            public pollDispatch?: (popclaw.event.IPollDispatch|null);

            /** EventEnvelope pollReport. */
            public pollReport?: (popclaw.event.IPollReport|null);

            /** EventEnvelope houseEvent. */
            public houseEvent?: (popclaw.event.IHouseEvent|null);

            /** EventEnvelope intent. */
            public intent?: (popclaw.event.IIntentPayload|null);

            /** EventEnvelope body. */
            public body?: ("inviteRequest"|"questDispatch"|"questResult"|"inviteVerified"|"rangerRegistration"|"watchDispatch"|"watchHeartbeat"|"watchCancel"|"followDeclared"|"followRevoked"|"reply"|"directMessage"|"post"|"profile"|"mark"|"markRevoked"|"pollDispatch"|"pollReport"|"houseEvent"|"intent");

            /**
             * Creates a new EventEnvelope instance using the specified properties.
             * @param [properties] Properties to set
             * @returns EventEnvelope instance
             */
            public static create(properties?: popclaw.event.IEventEnvelope): popclaw.event.EventEnvelope;

            /**
             * Encodes the specified EventEnvelope message. Does not implicitly {@link popclaw.event.EventEnvelope.verify|verify} messages.
             * @param message EventEnvelope message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IEventEnvelope, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an EventEnvelope message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns EventEnvelope
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.EventEnvelope;

            /**
             * Creates an EventEnvelope message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns EventEnvelope
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.EventEnvelope;

            /**
             * Creates a plain object from an EventEnvelope message. Also converts values to other types if specified.
             * @param message EventEnvelope
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.EventEnvelope, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this EventEnvelope to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for EventEnvelope
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ContentBlock. */
        interface IContentBlock {

            /** ContentBlock blockType */
            blockType?: (popclaw.event.ContentBlock.Type|null);

            /** ContentBlock content */
            content?: (string|null);

            /** ContentBlock metadata */
            metadata?: ({ [k: string]: string }|null);
        }

        /** Represents a ContentBlock. */
        class ContentBlock implements IContentBlock {

            /**
             * Constructs a new ContentBlock.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IContentBlock);

            /** ContentBlock blockType. */
            public blockType: popclaw.event.ContentBlock.Type;

            /** ContentBlock content. */
            public content: string;

            /** ContentBlock metadata. */
            public metadata: { [k: string]: string };

            /**
             * Creates a new ContentBlock instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ContentBlock instance
             */
            public static create(properties?: popclaw.event.IContentBlock): popclaw.event.ContentBlock;

            /**
             * Encodes the specified ContentBlock message. Does not implicitly {@link popclaw.event.ContentBlock.verify|verify} messages.
             * @param message ContentBlock message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IContentBlock, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ContentBlock message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ContentBlock
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.ContentBlock;

            /**
             * Creates a ContentBlock message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ContentBlock
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.ContentBlock;

            /**
             * Creates a plain object from a ContentBlock message. Also converts values to other types if specified.
             * @param message ContentBlock
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.ContentBlock, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ContentBlock to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ContentBlock
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        namespace ContentBlock {

            /** Type enum. */
            enum Type {
                TEXT = 0,
                IMAGE = 1,
                VIDEO = 2,
                LONG_FORM = 3,
                CODE_SNIPPET = 4,
                LINK_CARD = 5
            }
        }

        /** Properties of a MediaAttachment. */
        interface IMediaAttachment {

            /** MediaAttachment kind */
            kind?: (popclaw.event.MediaAttachment.Kind|null);

            /** MediaAttachment url */
            url?: (string|null);

            /** MediaAttachment width */
            width?: (number|null);

            /** MediaAttachment height */
            height?: (number|null);
        }

        /** Represents a MediaAttachment. */
        class MediaAttachment implements IMediaAttachment {

            /**
             * Constructs a new MediaAttachment.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IMediaAttachment);

            /** MediaAttachment kind. */
            public kind: popclaw.event.MediaAttachment.Kind;

            /** MediaAttachment url. */
            public url: string;

            /** MediaAttachment width. */
            public width?: (number|null);

            /** MediaAttachment height. */
            public height?: (number|null);

            /** MediaAttachment _width. */
            public _width?: "width";

            /** MediaAttachment _height. */
            public _height?: "height";

            /**
             * Creates a new MediaAttachment instance using the specified properties.
             * @param [properties] Properties to set
             * @returns MediaAttachment instance
             */
            public static create(properties?: popclaw.event.IMediaAttachment): popclaw.event.MediaAttachment;

            /**
             * Encodes the specified MediaAttachment message. Does not implicitly {@link popclaw.event.MediaAttachment.verify|verify} messages.
             * @param message MediaAttachment message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IMediaAttachment, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a MediaAttachment message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns MediaAttachment
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.MediaAttachment;

            /**
             * Creates a MediaAttachment message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns MediaAttachment
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.MediaAttachment;

            /**
             * Creates a plain object from a MediaAttachment message. Also converts values to other types if specified.
             * @param message MediaAttachment
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.MediaAttachment, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this MediaAttachment to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for MediaAttachment
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        namespace MediaAttachment {

            /** Kind enum. */
            enum Kind {
                IMAGE = 0,
                VIDEO = 1,
                GIF = 2
            }
        }

        /** Properties of a MetaStats. */
        interface IMetaStats {

            /** MetaStats likes */
            likes?: (number|Long|null);

            /** MetaStats shares */
            shares?: (number|Long|null);

            /** MetaStats comments */
            comments?: (number|Long|null);
        }

        /** Represents a MetaStats. */
        class MetaStats implements IMetaStats {

            /**
             * Constructs a new MetaStats.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IMetaStats);

            /** MetaStats likes. */
            public likes: (number|Long);

            /** MetaStats shares. */
            public shares: (number|Long);

            /** MetaStats comments. */
            public comments: (number|Long);

            /**
             * Creates a new MetaStats instance using the specified properties.
             * @param [properties] Properties to set
             * @returns MetaStats instance
             */
            public static create(properties?: popclaw.event.IMetaStats): popclaw.event.MetaStats;

            /**
             * Encodes the specified MetaStats message. Does not implicitly {@link popclaw.event.MetaStats.verify|verify} messages.
             * @param message MetaStats message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IMetaStats, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a MetaStats message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns MetaStats
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.MetaStats;

            /**
             * Creates a MetaStats message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns MetaStats
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.MetaStats;

            /**
             * Creates a plain object from a MetaStats message. Also converts values to other types if specified.
             * @param message MetaStats
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.MetaStats, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this MetaStats to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for MetaStats
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a DiscoveryFrame. */
        interface IDiscoveryFrame {

            /** DiscoveryFrame frameType */
            frameType?: (popclaw.event.DiscoveryFrame.FrameType|null);

            /** DiscoveryFrame event */
            event?: (popclaw.event.IEventEnvelope|null);
        }

        /** Represents a DiscoveryFrame. */
        class DiscoveryFrame implements IDiscoveryFrame {

            /**
             * Constructs a new DiscoveryFrame.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IDiscoveryFrame);

            /** DiscoveryFrame frameType. */
            public frameType: popclaw.event.DiscoveryFrame.FrameType;

            /** DiscoveryFrame event. */
            public event?: (popclaw.event.IEventEnvelope|null);

            /**
             * Creates a new DiscoveryFrame instance using the specified properties.
             * @param [properties] Properties to set
             * @returns DiscoveryFrame instance
             */
            public static create(properties?: popclaw.event.IDiscoveryFrame): popclaw.event.DiscoveryFrame;

            /**
             * Encodes the specified DiscoveryFrame message. Does not implicitly {@link popclaw.event.DiscoveryFrame.verify|verify} messages.
             * @param message DiscoveryFrame message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IDiscoveryFrame, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a DiscoveryFrame message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns DiscoveryFrame
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.DiscoveryFrame;

            /**
             * Creates a DiscoveryFrame message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns DiscoveryFrame
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.DiscoveryFrame;

            /**
             * Creates a plain object from a DiscoveryFrame message. Also converts values to other types if specified.
             * @param message DiscoveryFrame
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.DiscoveryFrame, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this DiscoveryFrame to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for DiscoveryFrame
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        namespace DiscoveryFrame {

            /** FrameType enum. */
            enum FrameType {
                EVENT = 0,
                HEARTBEAT = 1
            }
        }

        /** Properties of a RangerRegistration. */
        interface IRangerRegistration {

            /** RangerRegistration capabilities */
            capabilities?: (string[]|null);

            /** RangerRegistration availabilityScore */
            availabilityScore?: (number|null);
        }

        /** Represents a RangerRegistration. */
        class RangerRegistration implements IRangerRegistration {

            /**
             * Constructs a new RangerRegistration.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IRangerRegistration);

            /** RangerRegistration capabilities. */
            public capabilities: string[];

            /** RangerRegistration availabilityScore. */
            public availabilityScore: number;

            /**
             * Creates a new RangerRegistration instance using the specified properties.
             * @param [properties] Properties to set
             * @returns RangerRegistration instance
             */
            public static create(properties?: popclaw.event.IRangerRegistration): popclaw.event.RangerRegistration;

            /**
             * Encodes the specified RangerRegistration message. Does not implicitly {@link popclaw.event.RangerRegistration.verify|verify} messages.
             * @param message RangerRegistration message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IRangerRegistration, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a RangerRegistration message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns RangerRegistration
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.RangerRegistration;

            /**
             * Creates a RangerRegistration message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns RangerRegistration
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.RangerRegistration;

            /**
             * Creates a plain object from a RangerRegistration message. Also converts values to other types if specified.
             * @param message RangerRegistration
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.RangerRegistration, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this RangerRegistration to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for RangerRegistration
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a WatchDispatch. */
        interface IWatchDispatch {

            /** WatchDispatch watchId */
            watchId?: (string|null);

            /** WatchDispatch targetPopclawId */
            targetPopclawId?: (string|null);

            /** WatchDispatch platform */
            platform?: (string|null);

            /** WatchDispatch handle */
            handle?: (string|null);

            /** WatchDispatch since */
            since?: (number|Long|null);
        }

        /** Represents a WatchDispatch. */
        class WatchDispatch implements IWatchDispatch {

            /**
             * Constructs a new WatchDispatch.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IWatchDispatch);

            /** WatchDispatch watchId. */
            public watchId: string;

            /** WatchDispatch targetPopclawId. */
            public targetPopclawId: string;

            /** WatchDispatch platform. */
            public platform: string;

            /** WatchDispatch handle. */
            public handle: string;

            /** WatchDispatch since. */
            public since: (number|Long);

            /**
             * Creates a new WatchDispatch instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WatchDispatch instance
             */
            public static create(properties?: popclaw.event.IWatchDispatch): popclaw.event.WatchDispatch;

            /**
             * Encodes the specified WatchDispatch message. Does not implicitly {@link popclaw.event.WatchDispatch.verify|verify} messages.
             * @param message WatchDispatch message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IWatchDispatch, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WatchDispatch message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WatchDispatch
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.WatchDispatch;

            /**
             * Creates a WatchDispatch message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WatchDispatch
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.WatchDispatch;

            /**
             * Creates a plain object from a WatchDispatch message. Also converts values to other types if specified.
             * @param message WatchDispatch
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.WatchDispatch, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WatchDispatch to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WatchDispatch
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a WatchHeartbeat. */
        interface IWatchHeartbeat {

            /** WatchHeartbeat watchId */
            watchId?: (string|null);

            /** WatchHeartbeat activeSince */
            activeSince?: (number|Long|null);

            /** WatchHeartbeat recentHits */
            recentHits?: (number|null);
        }

        /** Represents a WatchHeartbeat. */
        class WatchHeartbeat implements IWatchHeartbeat {

            /**
             * Constructs a new WatchHeartbeat.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IWatchHeartbeat);

            /** WatchHeartbeat watchId. */
            public watchId: string;

            /** WatchHeartbeat activeSince. */
            public activeSince: (number|Long);

            /** WatchHeartbeat recentHits. */
            public recentHits: number;

            /**
             * Creates a new WatchHeartbeat instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WatchHeartbeat instance
             */
            public static create(properties?: popclaw.event.IWatchHeartbeat): popclaw.event.WatchHeartbeat;

            /**
             * Encodes the specified WatchHeartbeat message. Does not implicitly {@link popclaw.event.WatchHeartbeat.verify|verify} messages.
             * @param message WatchHeartbeat message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IWatchHeartbeat, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WatchHeartbeat message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WatchHeartbeat
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.WatchHeartbeat;

            /**
             * Creates a WatchHeartbeat message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WatchHeartbeat
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.WatchHeartbeat;

            /**
             * Creates a plain object from a WatchHeartbeat message. Also converts values to other types if specified.
             * @param message WatchHeartbeat
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.WatchHeartbeat, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WatchHeartbeat to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WatchHeartbeat
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a WatchCancel. */
        interface IWatchCancel {

            /** WatchCancel watchId */
            watchId?: (string|null);

            /** WatchCancel reason */
            reason?: (string|null);
        }

        /** Represents a WatchCancel. */
        class WatchCancel implements IWatchCancel {

            /**
             * Constructs a new WatchCancel.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IWatchCancel);

            /** WatchCancel watchId. */
            public watchId: string;

            /** WatchCancel reason. */
            public reason: string;

            /**
             * Creates a new WatchCancel instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WatchCancel instance
             */
            public static create(properties?: popclaw.event.IWatchCancel): popclaw.event.WatchCancel;

            /**
             * Encodes the specified WatchCancel message. Does not implicitly {@link popclaw.event.WatchCancel.verify|verify} messages.
             * @param message WatchCancel message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IWatchCancel, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WatchCancel message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WatchCancel
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.WatchCancel;

            /**
             * Creates a WatchCancel message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WatchCancel
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.WatchCancel;

            /**
             * Creates a plain object from a WatchCancel message. Also converts values to other types if specified.
             * @param message WatchCancel
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.WatchCancel, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WatchCancel to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WatchCancel
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a PollDispatch. */
        interface IPollDispatch {

            /** PollDispatch watchId */
            watchId?: (string|null);

            /** PollDispatch targetPopclawId */
            targetPopclawId?: (string|null);

            /** PollDispatch platform */
            platform?: (string|null);

            /** PollDispatch handle */
            handle?: (string|null);

            /** PollDispatch since */
            since?: (number|Long|null);
        }

        /** Represents a PollDispatch. */
        class PollDispatch implements IPollDispatch {

            /**
             * Constructs a new PollDispatch.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IPollDispatch);

            /** PollDispatch watchId. */
            public watchId: string;

            /** PollDispatch targetPopclawId. */
            public targetPopclawId: string;

            /** PollDispatch platform. */
            public platform: string;

            /** PollDispatch handle. */
            public handle: string;

            /** PollDispatch since. */
            public since: (number|Long);

            /**
             * Creates a new PollDispatch instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PollDispatch instance
             */
            public static create(properties?: popclaw.event.IPollDispatch): popclaw.event.PollDispatch;

            /**
             * Encodes the specified PollDispatch message. Does not implicitly {@link popclaw.event.PollDispatch.verify|verify} messages.
             * @param message PollDispatch message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IPollDispatch, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PollDispatch message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PollDispatch
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.PollDispatch;

            /**
             * Creates a PollDispatch message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PollDispatch
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.PollDispatch;

            /**
             * Creates a plain object from a PollDispatch message. Also converts values to other types if specified.
             * @param message PollDispatch
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.PollDispatch, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PollDispatch to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PollDispatch
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a PollReport. */
        interface IPollReport {

            /** PollReport watchId */
            watchId?: (string|null);

            /** PollReport result */
            result?: (popclaw.event.PollReport.Result|null);

            /** PollReport newestPostAt */
            newestPostAt?: (number|Long|null);

            /** PollReport newPostCount */
            newPostCount?: (number|null);
        }

        /** Represents a PollReport. */
        class PollReport implements IPollReport {

            /**
             * Constructs a new PollReport.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IPollReport);

            /** PollReport watchId. */
            public watchId: string;

            /** PollReport result. */
            public result: popclaw.event.PollReport.Result;

            /** PollReport newestPostAt. */
            public newestPostAt: (number|Long);

            /** PollReport newPostCount. */
            public newPostCount: number;

            /**
             * Creates a new PollReport instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PollReport instance
             */
            public static create(properties?: popclaw.event.IPollReport): popclaw.event.PollReport;

            /**
             * Encodes the specified PollReport message. Does not implicitly {@link popclaw.event.PollReport.verify|verify} messages.
             * @param message PollReport message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IPollReport, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PollReport message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PollReport
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.PollReport;

            /**
             * Creates a PollReport message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PollReport
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.PollReport;

            /**
             * Creates a plain object from a PollReport message. Also converts values to other types if specified.
             * @param message PollReport
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.PollReport, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PollReport to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PollReport
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        namespace PollReport {

            /** Result enum. */
            enum Result {
                POLL_EMPTY = 0,
                POLL_HIT = 1,
                POLL_FAILED = 2
            }
        }

        /** Properties of a WorldFeedItem. */
        interface IWorldFeedItem {

            /** WorldFeedItem platform */
            platform?: (string|null);

            /** WorldFeedItem platformPostId */
            platformPostId?: (string|null);

            /** WorldFeedItem platformPostCreatedAt */
            platformPostCreatedAt?: (number|Long|null);

            /** WorldFeedItem authorPopclawId */
            authorPopclawId?: (string|null);

            /** WorldFeedItem handle */
            handle?: (string|null);

            /** WorldFeedItem originalUrl */
            originalUrl?: (string|null);

            /** WorldFeedItem textPreview */
            textPreview?: (string|null);

            /** WorldFeedItem replyToPlatform */
            replyToPlatform?: (string|null);

            /** WorldFeedItem replyToPostId */
            replyToPostId?: (string|null);

            /** WorldFeedItem replyToAuthorPopclawId */
            replyToAuthorPopclawId?: (string|null);

            /** WorldFeedItem quotedEventId */
            quotedEventId?: (string|null);

            /** WorldFeedItem quotedAuthorPopclawId */
            quotedAuthorPopclawId?: (string|null);

            /** WorldFeedItem quotedAuthorHandle */
            quotedAuthorHandle?: (string|null);

            /** WorldFeedItem quotedTextPreview */
            quotedTextPreview?: (string|null);

            /** WorldFeedItem actorNickname */
            actorNickname?: (string|null);

            /** WorldFeedItem quotedActorNickname */
            quotedActorNickname?: (string|null);

            /** WorldFeedItem actorVerified */
            actorVerified?: (popclaw.event.IVerifiedPlatform[]|null);

            /** WorldFeedItem quotedActorVerified */
            quotedActorVerified?: (popclaw.event.IVerifiedPlatform[]|null);

            /** WorldFeedItem eventId */
            eventId?: (string|null);

            /** WorldFeedItem markCount */
            markCount?: (number|Long|null);

            /** WorldFeedItem origin */
            origin?: (popclaw.event.IOrigin|null);

            /** WorldFeedItem envelope */
            envelope?: (Uint8Array|null);

            /** WorldFeedItem replyToAuthorHandle */
            replyToAuthorHandle?: (string|null);

            /** WorldFeedItem replyToActorNickname */
            replyToActorNickname?: (string|null);

            /** WorldFeedItem replyCount */
            replyCount?: (number|Long|null);
        }

        /** Represents a WorldFeedItem. */
        class WorldFeedItem implements IWorldFeedItem {

            /**
             * Constructs a new WorldFeedItem.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IWorldFeedItem);

            /** WorldFeedItem platform. */
            public platform: string;

            /** WorldFeedItem platformPostId. */
            public platformPostId: string;

            /** WorldFeedItem platformPostCreatedAt. */
            public platformPostCreatedAt: (number|Long);

            /** WorldFeedItem authorPopclawId. */
            public authorPopclawId: string;

            /** WorldFeedItem handle. */
            public handle: string;

            /** WorldFeedItem originalUrl. */
            public originalUrl: string;

            /** WorldFeedItem textPreview. */
            public textPreview: string;

            /** WorldFeedItem replyToPlatform. */
            public replyToPlatform: string;

            /** WorldFeedItem replyToPostId. */
            public replyToPostId: string;

            /** WorldFeedItem replyToAuthorPopclawId. */
            public replyToAuthorPopclawId: string;

            /** WorldFeedItem quotedEventId. */
            public quotedEventId: string;

            /** WorldFeedItem quotedAuthorPopclawId. */
            public quotedAuthorPopclawId: string;

            /** WorldFeedItem quotedAuthorHandle. */
            public quotedAuthorHandle: string;

            /** WorldFeedItem quotedTextPreview. */
            public quotedTextPreview: string;

            /** WorldFeedItem actorNickname. */
            public actorNickname: string;

            /** WorldFeedItem quotedActorNickname. */
            public quotedActorNickname: string;

            /** WorldFeedItem actorVerified. */
            public actorVerified: popclaw.event.IVerifiedPlatform[];

            /** WorldFeedItem quotedActorVerified. */
            public quotedActorVerified: popclaw.event.IVerifiedPlatform[];

            /** WorldFeedItem eventId. */
            public eventId: string;

            /** WorldFeedItem markCount. */
            public markCount: (number|Long);

            /** WorldFeedItem origin. */
            public origin?: (popclaw.event.IOrigin|null);

            /** WorldFeedItem envelope. */
            public envelope: Uint8Array;

            /** WorldFeedItem replyToAuthorHandle. */
            public replyToAuthorHandle: string;

            /** WorldFeedItem replyToActorNickname. */
            public replyToActorNickname: string;

            /** WorldFeedItem replyCount. */
            public replyCount: (number|Long);

            /**
             * Creates a new WorldFeedItem instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WorldFeedItem instance
             */
            public static create(properties?: popclaw.event.IWorldFeedItem): popclaw.event.WorldFeedItem;

            /**
             * Encodes the specified WorldFeedItem message. Does not implicitly {@link popclaw.event.WorldFeedItem.verify|verify} messages.
             * @param message WorldFeedItem message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IWorldFeedItem, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WorldFeedItem message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WorldFeedItem
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.WorldFeedItem;

            /**
             * Creates a WorldFeedItem message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WorldFeedItem
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.WorldFeedItem;

            /**
             * Creates a plain object from a WorldFeedItem message. Also converts values to other types if specified.
             * @param message WorldFeedItem
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.WorldFeedItem, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WorldFeedItem to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WorldFeedItem
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a WorldFeedSnapshot. */
        interface IWorldFeedSnapshot {

            /** WorldFeedSnapshot items */
            items?: (popclaw.event.IWorldFeedItem[]|null);
        }

        /** Represents a WorldFeedSnapshot. */
        class WorldFeedSnapshot implements IWorldFeedSnapshot {

            /**
             * Constructs a new WorldFeedSnapshot.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IWorldFeedSnapshot);

            /** WorldFeedSnapshot items. */
            public items: popclaw.event.IWorldFeedItem[];

            /**
             * Creates a new WorldFeedSnapshot instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WorldFeedSnapshot instance
             */
            public static create(properties?: popclaw.event.IWorldFeedSnapshot): popclaw.event.WorldFeedSnapshot;

            /**
             * Encodes the specified WorldFeedSnapshot message. Does not implicitly {@link popclaw.event.WorldFeedSnapshot.verify|verify} messages.
             * @param message WorldFeedSnapshot message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IWorldFeedSnapshot, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WorldFeedSnapshot message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WorldFeedSnapshot
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.WorldFeedSnapshot;

            /**
             * Creates a WorldFeedSnapshot message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WorldFeedSnapshot
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.WorldFeedSnapshot;

            /**
             * Creates a plain object from a WorldFeedSnapshot message. Also converts values to other types if specified.
             * @param message WorldFeedSnapshot
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.WorldFeedSnapshot, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WorldFeedSnapshot to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WorldFeedSnapshot
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a WorldStreamFrame. */
        interface IWorldStreamFrame {

            /** WorldStreamFrame seq */
            seq?: (number|Long|null);

            /** WorldStreamFrame envelope */
            envelope?: (Uint8Array|null);

            /** WorldStreamFrame kind */
            kind?: (string|null);

            /** WorldStreamFrame projection */
            projection?: (popclaw.event.IWorldFeedItem|null);

            /** WorldStreamFrame scopes */
            scopes?: (string[]|null);
        }

        /** Represents a WorldStreamFrame. */
        class WorldStreamFrame implements IWorldStreamFrame {

            /**
             * Constructs a new WorldStreamFrame.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IWorldStreamFrame);

            /** WorldStreamFrame seq. */
            public seq: (number|Long);

            /** WorldStreamFrame envelope. */
            public envelope: Uint8Array;

            /** WorldStreamFrame kind. */
            public kind: string;

            /** WorldStreamFrame projection. */
            public projection?: (popclaw.event.IWorldFeedItem|null);

            /** WorldStreamFrame scopes. */
            public scopes: string[];

            /**
             * Creates a new WorldStreamFrame instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WorldStreamFrame instance
             */
            public static create(properties?: popclaw.event.IWorldStreamFrame): popclaw.event.WorldStreamFrame;

            /**
             * Encodes the specified WorldStreamFrame message. Does not implicitly {@link popclaw.event.WorldStreamFrame.verify|verify} messages.
             * @param message WorldStreamFrame message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IWorldStreamFrame, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WorldStreamFrame message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WorldStreamFrame
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.WorldStreamFrame;

            /**
             * Creates a WorldStreamFrame message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WorldStreamFrame
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.WorldStreamFrame;

            /**
             * Creates a plain object from a WorldStreamFrame message. Also converts values to other types if specified.
             * @param message WorldStreamFrame
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.WorldStreamFrame, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WorldStreamFrame to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WorldStreamFrame
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a VerifiedPlatform. */
        interface IVerifiedPlatform {

            /** VerifiedPlatform platform */
            platform?: (string|null);

            /** VerifiedPlatform handle */
            handle?: (string|null);

            /** VerifiedPlatform profileUrl */
            profileUrl?: (string|null);

            /** VerifiedPlatform followerCount */
            followerCount?: (number|Long|null);

            /** VerifiedPlatform accountId */
            accountId?: (string|null);
        }

        /** Represents a VerifiedPlatform. */
        class VerifiedPlatform implements IVerifiedPlatform {

            /**
             * Constructs a new VerifiedPlatform.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IVerifiedPlatform);

            /** VerifiedPlatform platform. */
            public platform: string;

            /** VerifiedPlatform handle. */
            public handle: string;

            /** VerifiedPlatform profileUrl. */
            public profileUrl: string;

            /** VerifiedPlatform followerCount. */
            public followerCount: (number|Long);

            /** VerifiedPlatform accountId. */
            public accountId: string;

            /**
             * Creates a new VerifiedPlatform instance using the specified properties.
             * @param [properties] Properties to set
             * @returns VerifiedPlatform instance
             */
            public static create(properties?: popclaw.event.IVerifiedPlatform): popclaw.event.VerifiedPlatform;

            /**
             * Encodes the specified VerifiedPlatform message. Does not implicitly {@link popclaw.event.VerifiedPlatform.verify|verify} messages.
             * @param message VerifiedPlatform message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IVerifiedPlatform, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a VerifiedPlatform message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns VerifiedPlatform
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.VerifiedPlatform;

            /**
             * Creates a VerifiedPlatform message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns VerifiedPlatform
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.VerifiedPlatform;

            /**
             * Creates a plain object from a VerifiedPlatform message. Also converts values to other types if specified.
             * @param message VerifiedPlatform
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.VerifiedPlatform, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this VerifiedPlatform to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for VerifiedPlatform
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a RelationOrder. */
        interface IRelationOrder {

            /** RelationOrder seq */
            seq?: (number|Long|null);

            /** RelationOrder houseKey */
            houseKey?: (string|null);

            /** RelationOrder resolves */
            resolves?: (string[]|null);
        }

        /** Represents a RelationOrder. */
        class RelationOrder implements IRelationOrder {

            /**
             * Constructs a new RelationOrder.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IRelationOrder);

            /** RelationOrder seq. */
            public seq: (number|Long);

            /** RelationOrder houseKey. */
            public houseKey: string;

            /** RelationOrder resolves. */
            public resolves: string[];

            /**
             * Creates a new RelationOrder instance using the specified properties.
             * @param [properties] Properties to set
             * @returns RelationOrder instance
             */
            public static create(properties?: popclaw.event.IRelationOrder): popclaw.event.RelationOrder;

            /**
             * Encodes the specified RelationOrder message. Does not implicitly {@link popclaw.event.RelationOrder.verify|verify} messages.
             * @param message RelationOrder message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IRelationOrder, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a RelationOrder message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns RelationOrder
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.RelationOrder;

            /**
             * Creates a RelationOrder message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns RelationOrder
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.RelationOrder;

            /**
             * Creates a plain object from a RelationOrder message. Also converts values to other types if specified.
             * @param message RelationOrder
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.RelationOrder, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this RelationOrder to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for RelationOrder
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a FollowDeclared. */
        interface IFollowDeclared {

            /** FollowDeclared followeePopclawId */
            followeePopclawId?: (string|null);

            /** FollowDeclared followType */
            followType?: (popclaw.event.FollowDeclared.FollowType|null);

            /** FollowDeclared tasteSubscribed */
            tasteSubscribed?: (boolean|null);

            /** FollowDeclared tasteSubscriptionVisibility */
            tasteSubscriptionVisibility?: (popclaw.event.FollowDeclared.SubscriptionVisibility|null);

            /** FollowDeclared order */
            order?: (popclaw.event.IRelationOrder|null);
        }

        /** Represents a FollowDeclared. */
        class FollowDeclared implements IFollowDeclared {

            /**
             * Constructs a new FollowDeclared.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IFollowDeclared);

            /** FollowDeclared followeePopclawId. */
            public followeePopclawId: string;

            /** FollowDeclared followType. */
            public followType: popclaw.event.FollowDeclared.FollowType;

            /** FollowDeclared tasteSubscribed. */
            public tasteSubscribed: boolean;

            /** FollowDeclared tasteSubscriptionVisibility. */
            public tasteSubscriptionVisibility: popclaw.event.FollowDeclared.SubscriptionVisibility;

            /** FollowDeclared order. */
            public order?: (popclaw.event.IRelationOrder|null);

            /**
             * Creates a new FollowDeclared instance using the specified properties.
             * @param [properties] Properties to set
             * @returns FollowDeclared instance
             */
            public static create(properties?: popclaw.event.IFollowDeclared): popclaw.event.FollowDeclared;

            /**
             * Encodes the specified FollowDeclared message. Does not implicitly {@link popclaw.event.FollowDeclared.verify|verify} messages.
             * @param message FollowDeclared message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IFollowDeclared, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a FollowDeclared message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns FollowDeclared
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.FollowDeclared;

            /**
             * Creates a FollowDeclared message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns FollowDeclared
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.FollowDeclared;

            /**
             * Creates a plain object from a FollowDeclared message. Also converts values to other types if specified.
             * @param message FollowDeclared
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.FollowDeclared, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this FollowDeclared to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for FollowDeclared
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        namespace FollowDeclared {

            /** FollowType enum. */
            enum FollowType {
                PUBLIC = 0,
                PRIVATE = 1
            }

            /** SubscriptionVisibility enum. */
            enum SubscriptionVisibility {
                SV_PUBLIC = 0,
                SV_PRIVATE = 1
            }
        }

        /** Properties of a FollowRevoked. */
        interface IFollowRevoked {

            /** FollowRevoked followeePopclawId */
            followeePopclawId?: (string|null);

            /** FollowRevoked followType */
            followType?: (popclaw.event.FollowRevoked.FollowType|null);

            /** FollowRevoked order */
            order?: (popclaw.event.IRelationOrder|null);
        }

        /** Represents a FollowRevoked. */
        class FollowRevoked implements IFollowRevoked {

            /**
             * Constructs a new FollowRevoked.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IFollowRevoked);

            /** FollowRevoked followeePopclawId. */
            public followeePopclawId: string;

            /** FollowRevoked followType. */
            public followType: popclaw.event.FollowRevoked.FollowType;

            /** FollowRevoked order. */
            public order?: (popclaw.event.IRelationOrder|null);

            /**
             * Creates a new FollowRevoked instance using the specified properties.
             * @param [properties] Properties to set
             * @returns FollowRevoked instance
             */
            public static create(properties?: popclaw.event.IFollowRevoked): popclaw.event.FollowRevoked;

            /**
             * Encodes the specified FollowRevoked message. Does not implicitly {@link popclaw.event.FollowRevoked.verify|verify} messages.
             * @param message FollowRevoked message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IFollowRevoked, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a FollowRevoked message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns FollowRevoked
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.FollowRevoked;

            /**
             * Creates a FollowRevoked message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns FollowRevoked
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.FollowRevoked;

            /**
             * Creates a plain object from a FollowRevoked message. Also converts values to other types if specified.
             * @param message FollowRevoked
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.FollowRevoked, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this FollowRevoked to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for FollowRevoked
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        namespace FollowRevoked {

            /** FollowType enum. */
            enum FollowType {
                PUBLIC = 0,
                PRIVATE = 1
            }
        }

        /** Properties of a PostRef. */
        interface IPostRef {

            /** PostRef platform */
            platform?: (string|null);

            /** PostRef platformPostId */
            platformPostId?: (string|null);

            /** PostRef authorPopclawId */
            authorPopclawId?: (string|null);
        }

        /** Represents a PostRef. */
        class PostRef implements IPostRef {

            /**
             * Constructs a new PostRef.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IPostRef);

            /** PostRef platform. */
            public platform: string;

            /** PostRef platformPostId. */
            public platformPostId: string;

            /** PostRef authorPopclawId. */
            public authorPopclawId: string;

            /**
             * Creates a new PostRef instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PostRef instance
             */
            public static create(properties?: popclaw.event.IPostRef): popclaw.event.PostRef;

            /**
             * Encodes the specified PostRef message. Does not implicitly {@link popclaw.event.PostRef.verify|verify} messages.
             * @param message PostRef message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IPostRef, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PostRef message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PostRef
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.PostRef;

            /**
             * Creates a PostRef message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PostRef
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.PostRef;

            /**
             * Creates a plain object from a PostRef message. Also converts values to other types if specified.
             * @param message PostRef
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.PostRef, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PostRef to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PostRef
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a Reply. */
        interface IReply {

            /** Reply fromPopclawId */
            fromPopclawId?: (string|null);

            /** Reply inReplyTo */
            inReplyTo?: (popclaw.event.IPostRef|null);

            /** Reply body */
            body?: (string|null);

            /** Reply ts */
            ts?: (number|Long|null);
        }

        /** Represents a Reply. */
        class Reply implements IReply {

            /**
             * Constructs a new Reply.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IReply);

            /** Reply fromPopclawId. */
            public fromPopclawId: string;

            /** Reply inReplyTo. */
            public inReplyTo?: (popclaw.event.IPostRef|null);

            /** Reply body. */
            public body: string;

            /** Reply ts. */
            public ts: (number|Long);

            /**
             * Creates a new Reply instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Reply instance
             */
            public static create(properties?: popclaw.event.IReply): popclaw.event.Reply;

            /**
             * Encodes the specified Reply message. Does not implicitly {@link popclaw.event.Reply.verify|verify} messages.
             * @param message Reply message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IReply, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Reply message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns Reply
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.Reply;

            /**
             * Creates a Reply message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Reply
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.Reply;

            /**
             * Creates a plain object from a Reply message. Also converts values to other types if specified.
             * @param message Reply
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.Reply, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Reply to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for Reply
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a DirectMessage. */
        interface IDirectMessage {

            /** DirectMessage fromPopclawId */
            fromPopclawId?: (string|null);

            /** DirectMessage toPopclawId */
            toPopclawId?: (string|null);

            /** DirectMessage inReplyToPost */
            inReplyToPost?: (popclaw.event.IPostRef|null);

            /** DirectMessage body */
            body?: (string|null);

            /** DirectMessage ts */
            ts?: (number|Long|null);

            /** DirectMessage ciphertext */
            ciphertext?: (Uint8Array|null);

            /** DirectMessage nonce */
            nonce?: (Uint8Array|null);

            /** DirectMessage mediaCiphertext */
            mediaCiphertext?: (Uint8Array|null);

            /** DirectMessage mediaNonce */
            mediaNonce?: (Uint8Array|null);
        }

        /** Represents a DirectMessage. */
        class DirectMessage implements IDirectMessage {

            /**
             * Constructs a new DirectMessage.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IDirectMessage);

            /** DirectMessage fromPopclawId. */
            public fromPopclawId: string;

            /** DirectMessage toPopclawId. */
            public toPopclawId: string;

            /** DirectMessage inReplyToPost. */
            public inReplyToPost?: (popclaw.event.IPostRef|null);

            /** DirectMessage body. */
            public body: string;

            /** DirectMessage ts. */
            public ts: (number|Long);

            /** DirectMessage ciphertext. */
            public ciphertext: Uint8Array;

            /** DirectMessage nonce. */
            public nonce: Uint8Array;

            /** DirectMessage mediaCiphertext. */
            public mediaCiphertext: Uint8Array;

            /** DirectMessage mediaNonce. */
            public mediaNonce: Uint8Array;

            /**
             * Creates a new DirectMessage instance using the specified properties.
             * @param [properties] Properties to set
             * @returns DirectMessage instance
             */
            public static create(properties?: popclaw.event.IDirectMessage): popclaw.event.DirectMessage;

            /**
             * Encodes the specified DirectMessage message. Does not implicitly {@link popclaw.event.DirectMessage.verify|verify} messages.
             * @param message DirectMessage message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IDirectMessage, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a DirectMessage message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns DirectMessage
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.DirectMessage;

            /**
             * Creates a DirectMessage message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns DirectMessage
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.DirectMessage;

            /**
             * Creates a plain object from a DirectMessage message. Also converts values to other types if specified.
             * @param message DirectMessage
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.DirectMessage, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this DirectMessage to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for DirectMessage
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a Mark. */
        interface IMark {

            /** Mark markedEventId */
            markedEventId?: (string|null);
        }

        /** Represents a Mark. */
        class Mark implements IMark {

            /**
             * Constructs a new Mark.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IMark);

            /** Mark markedEventId. */
            public markedEventId: string;

            /**
             * Creates a new Mark instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Mark instance
             */
            public static create(properties?: popclaw.event.IMark): popclaw.event.Mark;

            /**
             * Encodes the specified Mark message. Does not implicitly {@link popclaw.event.Mark.verify|verify} messages.
             * @param message Mark message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IMark, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Mark message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns Mark
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.Mark;

            /**
             * Creates a Mark message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Mark
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.Mark;

            /**
             * Creates a plain object from a Mark message. Also converts values to other types if specified.
             * @param message Mark
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.Mark, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Mark to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for Mark
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a MarkRevoked. */
        interface IMarkRevoked {

            /** MarkRevoked markedEventId */
            markedEventId?: (string|null);
        }

        /** Represents a MarkRevoked. */
        class MarkRevoked implements IMarkRevoked {

            /**
             * Constructs a new MarkRevoked.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IMarkRevoked);

            /** MarkRevoked markedEventId. */
            public markedEventId: string;

            /**
             * Creates a new MarkRevoked instance using the specified properties.
             * @param [properties] Properties to set
             * @returns MarkRevoked instance
             */
            public static create(properties?: popclaw.event.IMarkRevoked): popclaw.event.MarkRevoked;

            /**
             * Encodes the specified MarkRevoked message. Does not implicitly {@link popclaw.event.MarkRevoked.verify|verify} messages.
             * @param message MarkRevoked message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IMarkRevoked, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a MarkRevoked message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns MarkRevoked
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.MarkRevoked;

            /**
             * Creates a MarkRevoked message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns MarkRevoked
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.MarkRevoked;

            /**
             * Creates a plain object from a MarkRevoked message. Also converts values to other types if specified.
             * @param message MarkRevoked
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.MarkRevoked, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this MarkRevoked to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for MarkRevoked
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an Origin. */
        interface IOrigin {

            /** Origin platform */
            platform?: (string|null);

            /** Origin postId */
            postId?: (string|null);

            /** Origin url */
            url?: (string|null);

            /** Origin createdAt */
            createdAt?: (number|Long|null);

            /** Origin replyToId */
            replyToId?: (string|null);
        }

        /** Represents an Origin. */
        class Origin implements IOrigin {

            /**
             * Constructs a new Origin.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IOrigin);

            /** Origin platform. */
            public platform: string;

            /** Origin postId. */
            public postId: string;

            /** Origin url. */
            public url: string;

            /** Origin createdAt. */
            public createdAt: (number|Long);

            /** Origin replyToId. */
            public replyToId: string;

            /**
             * Creates a new Origin instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Origin instance
             */
            public static create(properties?: popclaw.event.IOrigin): popclaw.event.Origin;

            /**
             * Encodes the specified Origin message. Does not implicitly {@link popclaw.event.Origin.verify|verify} messages.
             * @param message Origin message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IOrigin, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an Origin message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns Origin
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.Origin;

            /**
             * Creates an Origin message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Origin
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.Origin;

            /**
             * Creates a plain object from an Origin message. Also converts values to other types if specified.
             * @param message Origin
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.Origin, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Origin to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for Origin
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a Post. */
        interface IPost {

            /** Post blocks */
            blocks?: (popclaw.event.IContentBlock[]|null);

            /** Post media */
            media?: (popclaw.event.IMediaAttachment[]|null);

            /** Post origin */
            origin?: (popclaw.event.IOrigin|null);
        }

        /** Represents a Post. */
        class Post implements IPost {

            /**
             * Constructs a new Post.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IPost);

            /** Post blocks. */
            public blocks: popclaw.event.IContentBlock[];

            /** Post media. */
            public media: popclaw.event.IMediaAttachment[];

            /** Post origin. */
            public origin?: (popclaw.event.IOrigin|null);

            /**
             * Creates a new Post instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Post instance
             */
            public static create(properties?: popclaw.event.IPost): popclaw.event.Post;

            /**
             * Encodes the specified Post message. Does not implicitly {@link popclaw.event.Post.verify|verify} messages.
             * @param message Post message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IPost, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Post message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns Post
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.Post;

            /**
             * Creates a Post message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Post
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.Post;

            /**
             * Creates a plain object from a Post message. Also converts values to other types if specified.
             * @param message Post
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.Post, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Post to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for Post
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an HouseEvent. */
        interface IHouseEvent {

            /** HouseEvent kind */
            kind?: (string|null);

            /** HouseEvent schemaVersion */
            schemaVersion?: (number|null);

            /** HouseEvent body */
            body?: (Uint8Array|null);

            /** HouseEvent publicScopes */
            publicScopes?: (string[]|null);
        }

        /** Represents an HouseEvent. */
        class HouseEvent implements IHouseEvent {

            /**
             * Constructs a new HouseEvent.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IHouseEvent);

            /** HouseEvent kind. */
            public kind: string;

            /** HouseEvent schemaVersion. */
            public schemaVersion: number;

            /** HouseEvent body. */
            public body: Uint8Array;

            /** HouseEvent publicScopes. */
            public publicScopes: string[];

            /**
             * Creates a new HouseEvent instance using the specified properties.
             * @param [properties] Properties to set
             * @returns HouseEvent instance
             */
            public static create(properties?: popclaw.event.IHouseEvent): popclaw.event.HouseEvent;

            /**
             * Encodes the specified HouseEvent message. Does not implicitly {@link popclaw.event.HouseEvent.verify|verify} messages.
             * @param message HouseEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IHouseEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an HouseEvent message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns HouseEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.HouseEvent;

            /**
             * Creates an HouseEvent message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns HouseEvent
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.HouseEvent;

            /**
             * Creates a plain object from an HouseEvent message. Also converts values to other types if specified.
             * @param message HouseEvent
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.HouseEvent, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this HouseEvent to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for HouseEvent
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an IntentPayload. */
        interface IIntentPayload {

            /** IntentPayload lorehouse */
            lorehouse?: (string|null);

            /** IntentPayload intentKind */
            intentKind?: (string|null);

            /** IntentPayload params */
            params?: (Uint8Array|null);

            /** IntentPayload context */
            context?: (popclaw.world.IIntentContext|null);
        }

        /** Represents an IntentPayload. */
        class IntentPayload implements IIntentPayload {

            /**
             * Constructs a new IntentPayload.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.event.IIntentPayload);

            /** IntentPayload lorehouse. */
            public lorehouse: string;

            /** IntentPayload intentKind. */
            public intentKind: string;

            /** IntentPayload params. */
            public params: Uint8Array;

            /** IntentPayload context. */
            public context?: (popclaw.world.IIntentContext|null);

            /**
             * Creates a new IntentPayload instance using the specified properties.
             * @param [properties] Properties to set
             * @returns IntentPayload instance
             */
            public static create(properties?: popclaw.event.IIntentPayload): popclaw.event.IntentPayload;

            /**
             * Encodes the specified IntentPayload message. Does not implicitly {@link popclaw.event.IntentPayload.verify|verify} messages.
             * @param message IntentPayload message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.event.IIntentPayload, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an IntentPayload message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns IntentPayload
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.event.IntentPayload;

            /**
             * Creates an IntentPayload message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns IntentPayload
             */
            public static fromObject(object: { [k: string]: any }): popclaw.event.IntentPayload;

            /**
             * Creates a plain object from an IntentPayload message. Also converts values to other types if specified.
             * @param message IntentPayload
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.event.IntentPayload, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this IntentPayload to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for IntentPayload
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }
    }

    /** Namespace invite. */
    namespace invite {

        /** InviteVerificationMode enum. */
        enum InviteVerificationMode {
            INVITE_VERIFICATION_MODE_LOOKUP_ONCE = 0,
            INVITE_VERIFICATION_MODE_WAIT_NEW_POST = 1
        }

        /** Properties of an InviteRequest. */
        interface IInviteRequest {

            /** InviteRequest platform */
            platform?: (string|null);

            /** InviteRequest handle */
            handle?: (string|null);

            /** InviteRequest nickname */
            nickname?: (string|null);

            /** InviteRequest landingUrl */
            landingUrl?: (string|null);

            /** InviteRequest replace */
            replace?: (boolean|null);

            /** InviteRequest proofUrl */
            proofUrl?: (string|null);

            /** InviteRequest mirrorOptin */
            mirrorOptin?: (boolean|null);

            /** InviteRequest verificationMode */
            verificationMode?: (popclaw.invite.InviteVerificationMode|null);

            /** InviteRequest cancelTaskId */
            cancelTaskId?: (string|null);
        }

        /** Represents an InviteRequest. */
        class InviteRequest implements IInviteRequest {

            /**
             * Constructs a new InviteRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.invite.IInviteRequest);

            /** InviteRequest platform. */
            public platform: string;

            /** InviteRequest handle. */
            public handle: string;

            /** InviteRequest nickname. */
            public nickname: string;

            /** InviteRequest landingUrl. */
            public landingUrl: string;

            /** InviteRequest replace. */
            public replace: boolean;

            /** InviteRequest proofUrl. */
            public proofUrl: string;

            /** InviteRequest mirrorOptin. */
            public mirrorOptin: boolean;

            /** InviteRequest verificationMode. */
            public verificationMode: popclaw.invite.InviteVerificationMode;

            /** InviteRequest cancelTaskId. */
            public cancelTaskId: string;

            /**
             * Creates a new InviteRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns InviteRequest instance
             */
            public static create(properties?: popclaw.invite.IInviteRequest): popclaw.invite.InviteRequest;

            /**
             * Encodes the specified InviteRequest message. Does not implicitly {@link popclaw.invite.InviteRequest.verify|verify} messages.
             * @param message InviteRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.invite.IInviteRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an InviteRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns InviteRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.invite.InviteRequest;

            /**
             * Creates an InviteRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns InviteRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.invite.InviteRequest;

            /**
             * Creates a plain object from an InviteRequest message. Also converts values to other types if specified.
             * @param message InviteRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.invite.InviteRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this InviteRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for InviteRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an InviteVerified. */
        interface IInviteVerified {

            /** InviteVerified taskId */
            taskId?: (string|null);

            /** InviteVerified applicantPopclawId */
            applicantPopclawId?: (Uint8Array|null);

            /** InviteVerified platform */
            platform?: (string|null);

            /** InviteVerified handle */
            handle?: (string|null);

            /** InviteVerified approveCount */
            approveCount?: (number|null);

            /** InviteVerified rejectCount */
            rejectCount?: (number|null);

            /** InviteVerified followerCount */
            followerCount?: (number|Long|null);

            /** InviteVerified accountId */
            accountId?: (string|null);
        }

        /** Represents an InviteVerified. */
        class InviteVerified implements IInviteVerified {

            /**
             * Constructs a new InviteVerified.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.invite.IInviteVerified);

            /** InviteVerified taskId. */
            public taskId: string;

            /** InviteVerified applicantPopclawId. */
            public applicantPopclawId: Uint8Array;

            /** InviteVerified platform. */
            public platform: string;

            /** InviteVerified handle. */
            public handle: string;

            /** InviteVerified approveCount. */
            public approveCount: number;

            /** InviteVerified rejectCount. */
            public rejectCount: number;

            /** InviteVerified followerCount. */
            public followerCount: (number|Long);

            /** InviteVerified accountId. */
            public accountId: string;

            /**
             * Creates a new InviteVerified instance using the specified properties.
             * @param [properties] Properties to set
             * @returns InviteVerified instance
             */
            public static create(properties?: popclaw.invite.IInviteVerified): popclaw.invite.InviteVerified;

            /**
             * Encodes the specified InviteVerified message. Does not implicitly {@link popclaw.invite.InviteVerified.verify|verify} messages.
             * @param message InviteVerified message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.invite.IInviteVerified, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an InviteVerified message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns InviteVerified
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.invite.InviteVerified;

            /**
             * Creates an InviteVerified message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns InviteVerified
             */
            public static fromObject(object: { [k: string]: any }): popclaw.invite.InviteVerified;

            /**
             * Creates a plain object from an InviteVerified message. Also converts values to other types if specified.
             * @param message InviteVerified
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.invite.InviteVerified, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this InviteVerified to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for InviteVerified
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }
    }

    /** Namespace quest. */
    namespace quest {

        /** QuestKind enum. */
        enum QuestKind {
            QUEST_KIND_UNSPECIFIED = 0,
            QUEST_KIND_VERIFY_INVITE = 1,
            QUEST_KIND_SCRAPE_CONTENT = 2
        }

        /** QuestOutcome enum. */
        enum QuestOutcome {
            QUEST_OUTCOME_UNSPECIFIED = 0,
            QUEST_OUTCOME_APPROVE = 1,
            QUEST_OUTCOME_REJECT = 2,
            QUEST_OUTCOME_ABSTAIN = 3
        }

        /** InviteVerificationProgress enum. */
        enum InviteVerificationProgress {
            INVITE_VERIFICATION_PROGRESS_UNSPECIFIED = 0,
            INVITE_VERIFICATION_PROGRESS_PREPARING = 1,
            INVITE_VERIFICATION_PROGRESS_READY = 2,
            INVITE_VERIFICATION_PROGRESS_RECOVERING = 3
        }

        /** Properties of a VerifyInvitePayload. */
        interface IVerifyInvitePayload {

            /** VerifyInvitePayload platform */
            platform?: (string|null);

            /** VerifyInvitePayload handle */
            handle?: (string|null);

            /** VerifyInvitePayload applicantPopclawId */
            applicantPopclawId?: (Uint8Array|null);

            /** VerifyInvitePayload expectedSigil */
            expectedSigil?: (string|null);

            /** VerifyInvitePayload proofUrl */
            proofUrl?: (string|null);

            /** VerifyInvitePayload verificationMode */
            verificationMode?: (popclaw.invite.InviteVerificationMode|null);
        }

        /** Represents a VerifyInvitePayload. */
        class VerifyInvitePayload implements IVerifyInvitePayload {

            /**
             * Constructs a new VerifyInvitePayload.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.quest.IVerifyInvitePayload);

            /** VerifyInvitePayload platform. */
            public platform: string;

            /** VerifyInvitePayload handle. */
            public handle: string;

            /** VerifyInvitePayload applicantPopclawId. */
            public applicantPopclawId: Uint8Array;

            /** VerifyInvitePayload expectedSigil. */
            public expectedSigil: string;

            /** VerifyInvitePayload proofUrl. */
            public proofUrl: string;

            /** VerifyInvitePayload verificationMode. */
            public verificationMode: popclaw.invite.InviteVerificationMode;

            /**
             * Creates a new VerifyInvitePayload instance using the specified properties.
             * @param [properties] Properties to set
             * @returns VerifyInvitePayload instance
             */
            public static create(properties?: popclaw.quest.IVerifyInvitePayload): popclaw.quest.VerifyInvitePayload;

            /**
             * Encodes the specified VerifyInvitePayload message. Does not implicitly {@link popclaw.quest.VerifyInvitePayload.verify|verify} messages.
             * @param message VerifyInvitePayload message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.quest.IVerifyInvitePayload, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a VerifyInvitePayload message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns VerifyInvitePayload
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.quest.VerifyInvitePayload;

            /**
             * Creates a VerifyInvitePayload message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns VerifyInvitePayload
             */
            public static fromObject(object: { [k: string]: any }): popclaw.quest.VerifyInvitePayload;

            /**
             * Creates a plain object from a VerifyInvitePayload message. Also converts values to other types if specified.
             * @param message VerifyInvitePayload
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.quest.VerifyInvitePayload, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this VerifyInvitePayload to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for VerifyInvitePayload
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ScrapeContentPayload. */
        interface IScrapeContentPayload {

            /** ScrapeContentPayload platform */
            platform?: (string|null);

            /** ScrapeContentPayload handle */
            handle?: (string|null);

            /** ScrapeContentPayload sinceTimestamp */
            sinceTimestamp?: (number|Long|null);

            /** ScrapeContentPayload maxItems */
            maxItems?: (number|null);
        }

        /** Represents a ScrapeContentPayload. */
        class ScrapeContentPayload implements IScrapeContentPayload {

            /**
             * Constructs a new ScrapeContentPayload.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.quest.IScrapeContentPayload);

            /** ScrapeContentPayload platform. */
            public platform: string;

            /** ScrapeContentPayload handle. */
            public handle: string;

            /** ScrapeContentPayload sinceTimestamp. */
            public sinceTimestamp: (number|Long);

            /** ScrapeContentPayload maxItems. */
            public maxItems: number;

            /**
             * Creates a new ScrapeContentPayload instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ScrapeContentPayload instance
             */
            public static create(properties?: popclaw.quest.IScrapeContentPayload): popclaw.quest.ScrapeContentPayload;

            /**
             * Encodes the specified ScrapeContentPayload message. Does not implicitly {@link popclaw.quest.ScrapeContentPayload.verify|verify} messages.
             * @param message ScrapeContentPayload message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.quest.IScrapeContentPayload, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ScrapeContentPayload message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ScrapeContentPayload
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.quest.ScrapeContentPayload;

            /**
             * Creates a ScrapeContentPayload message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ScrapeContentPayload
             */
            public static fromObject(object: { [k: string]: any }): popclaw.quest.ScrapeContentPayload;

            /**
             * Creates a plain object from a ScrapeContentPayload message. Also converts values to other types if specified.
             * @param message ScrapeContentPayload
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.quest.ScrapeContentPayload, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ScrapeContentPayload to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ScrapeContentPayload
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a QuestDispatch. */
        interface IQuestDispatch {

            /** QuestDispatch taskId */
            taskId?: (string|null);

            /** QuestDispatch kind */
            kind?: (popclaw.quest.QuestKind|null);

            /** QuestDispatch expiresAt */
            expiresAt?: (number|Long|null);

            /** QuestDispatch verifyInvite */
            verifyInvite?: (popclaw.quest.IVerifyInvitePayload|null);

            /** QuestDispatch scrapeContent */
            scrapeContent?: (popclaw.quest.IScrapeContentPayload|null);
        }

        /** Represents a QuestDispatch. */
        class QuestDispatch implements IQuestDispatch {

            /**
             * Constructs a new QuestDispatch.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.quest.IQuestDispatch);

            /** QuestDispatch taskId. */
            public taskId: string;

            /** QuestDispatch kind. */
            public kind: popclaw.quest.QuestKind;

            /** QuestDispatch expiresAt. */
            public expiresAt: (number|Long);

            /** QuestDispatch verifyInvite. */
            public verifyInvite?: (popclaw.quest.IVerifyInvitePayload|null);

            /** QuestDispatch scrapeContent. */
            public scrapeContent?: (popclaw.quest.IScrapeContentPayload|null);

            /** QuestDispatch quest. */
            public quest?: ("verifyInvite"|"scrapeContent");

            /**
             * Creates a new QuestDispatch instance using the specified properties.
             * @param [properties] Properties to set
             * @returns QuestDispatch instance
             */
            public static create(properties?: popclaw.quest.IQuestDispatch): popclaw.quest.QuestDispatch;

            /**
             * Encodes the specified QuestDispatch message. Does not implicitly {@link popclaw.quest.QuestDispatch.verify|verify} messages.
             * @param message QuestDispatch message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.quest.IQuestDispatch, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a QuestDispatch message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns QuestDispatch
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.quest.QuestDispatch;

            /**
             * Creates a QuestDispatch message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns QuestDispatch
             */
            public static fromObject(object: { [k: string]: any }): popclaw.quest.QuestDispatch;

            /**
             * Creates a plain object from a QuestDispatch message. Also converts values to other types if specified.
             * @param message QuestDispatch
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.quest.QuestDispatch, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this QuestDispatch to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for QuestDispatch
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a QuestResult. */
        interface IQuestResult {

            /** QuestResult taskId */
            taskId?: (string|null);

            /** QuestResult outcome */
            outcome?: (popclaw.quest.QuestOutcome|null);

            /** QuestResult evidenceHash */
            evidenceHash?: (Uint8Array|null);

            /** QuestResult evidenceSample */
            evidenceSample?: (Uint8Array|null);

            /** QuestResult reason */
            reason?: (string|null);

            /** QuestResult accountId */
            accountId?: (string|null);

            /** QuestResult followerCount */
            followerCount?: (number|Long|null);

            /** QuestResult avatarUrl */
            avatarUrl?: (string|null);

            /** QuestResult bio */
            bio?: (string|null);

            /** QuestResult verificationProgress */
            verificationProgress?: (popclaw.quest.InviteVerificationProgress|null);

            /** QuestResult progressRevision */
            progressRevision?: (number|Long|null);
        }

        /** Represents a QuestResult. */
        class QuestResult implements IQuestResult {

            /**
             * Constructs a new QuestResult.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.quest.IQuestResult);

            /** QuestResult taskId. */
            public taskId: string;

            /** QuestResult outcome. */
            public outcome: popclaw.quest.QuestOutcome;

            /** QuestResult evidenceHash. */
            public evidenceHash: Uint8Array;

            /** QuestResult evidenceSample. */
            public evidenceSample: Uint8Array;

            /** QuestResult reason. */
            public reason: string;

            /** QuestResult accountId. */
            public accountId: string;

            /** QuestResult followerCount. */
            public followerCount: (number|Long);

            /** QuestResult avatarUrl. */
            public avatarUrl: string;

            /** QuestResult bio. */
            public bio: string;

            /** QuestResult verificationProgress. */
            public verificationProgress: popclaw.quest.InviteVerificationProgress;

            /** QuestResult progressRevision. */
            public progressRevision: (number|Long);

            /**
             * Creates a new QuestResult instance using the specified properties.
             * @param [properties] Properties to set
             * @returns QuestResult instance
             */
            public static create(properties?: popclaw.quest.IQuestResult): popclaw.quest.QuestResult;

            /**
             * Encodes the specified QuestResult message. Does not implicitly {@link popclaw.quest.QuestResult.verify|verify} messages.
             * @param message QuestResult message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.quest.IQuestResult, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a QuestResult message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns QuestResult
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.quest.QuestResult;

            /**
             * Creates a QuestResult message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns QuestResult
             */
            public static fromObject(object: { [k: string]: any }): popclaw.quest.QuestResult;

            /**
             * Creates a plain object from a QuestResult message. Also converts values to other types if specified.
             * @param message QuestResult
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.quest.QuestResult, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this QuestResult to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for QuestResult
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }
    }

    /** Namespace profile. */
    namespace profile {

        /** Properties of a Profile. */
        interface IProfile {

            /** Profile nickname */
            nickname?: (string|null);

            /** Profile oneLineIntro */
            oneLineIntro?: (string|null);

            /** Profile tasteTags */
            tasteTags?: (string[]|null);

            /** Profile rolePersona */
            rolePersona?: (string|null);

            /** Profile locationHint */
            locationHint?: (string|null);

            /** Profile avatarUri */
            avatarUri?: (string|null);

            /** Profile declaredAt */
            declaredAt?: (number|Long|null);
        }

        /** Represents a Profile. */
        class Profile implements IProfile {

            /**
             * Constructs a new Profile.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.profile.IProfile);

            /** Profile nickname. */
            public nickname: string;

            /** Profile oneLineIntro. */
            public oneLineIntro: string;

            /** Profile tasteTags. */
            public tasteTags: string[];

            /** Profile rolePersona. */
            public rolePersona: string;

            /** Profile locationHint. */
            public locationHint: string;

            /** Profile avatarUri. */
            public avatarUri: string;

            /** Profile declaredAt. */
            public declaredAt: (number|Long);

            /**
             * Creates a new Profile instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Profile instance
             */
            public static create(properties?: popclaw.profile.IProfile): popclaw.profile.Profile;

            /**
             * Encodes the specified Profile message. Does not implicitly {@link popclaw.profile.Profile.verify|verify} messages.
             * @param message Profile message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.profile.IProfile, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Profile message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns Profile
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.profile.Profile;

            /**
             * Creates a Profile message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Profile
             */
            public static fromObject(object: { [k: string]: any }): popclaw.profile.Profile;

            /**
             * Creates a plain object from a Profile message. Also converts values to other types if specified.
             * @param message Profile
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.profile.Profile, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Profile to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for Profile
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }
    }

    /** Namespace world. */
    namespace world {

        /** Properties of an HouseBinding. */
        interface IHouseBinding {

            /** HouseBinding origin */
            origin?: (string|null);

            /** HouseBinding houseKey */
            houseKey?: (string|null);

            /** HouseBinding incarnation */
            incarnation?: (string|null);
        }

        /** Represents an HouseBinding. */
        class HouseBinding implements IHouseBinding {

            /**
             * Constructs a new HouseBinding.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IHouseBinding);

            /** HouseBinding origin. */
            public origin: string;

            /** HouseBinding houseKey. */
            public houseKey: string;

            /** HouseBinding incarnation. */
            public incarnation: string;

            /**
             * Creates a new HouseBinding instance using the specified properties.
             * @param [properties] Properties to set
             * @returns HouseBinding instance
             */
            public static create(properties?: popclaw.world.IHouseBinding): popclaw.world.HouseBinding;

            /**
             * Encodes the specified HouseBinding message. Does not implicitly {@link popclaw.world.HouseBinding.verify|verify} messages.
             * @param message HouseBinding message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IHouseBinding, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an HouseBinding message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns HouseBinding
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.HouseBinding;

            /**
             * Creates an HouseBinding message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns HouseBinding
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.HouseBinding;

            /**
             * Creates a plain object from an HouseBinding message. Also converts values to other types if specified.
             * @param message HouseBinding
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.HouseBinding, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this HouseBinding to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for HouseBinding
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an IntentContext. */
        interface IIntentContext {

            /** IntentContext houseOrigin */
            houseOrigin?: (string|null);

            /** IntentContext houseKey */
            houseKey?: (string|null);

            /** IntentContext incarnation */
            incarnation?: (string|null);

            /** IntentContext sessionId */
            sessionId?: (string|null);

            /** IntentContext fence */
            fence?: (string|null);

            /** IntentContext capabilityRevision */
            capabilityRevision?: (string|null);

            /** IntentContext schemaVersion */
            schemaVersion?: (number|null);

            /** IntentContext validUntil */
            validUntil?: (number|Long|null);
        }

        /** Represents an IntentContext. */
        class IntentContext implements IIntentContext {

            /**
             * Constructs a new IntentContext.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IIntentContext);

            /** IntentContext houseOrigin. */
            public houseOrigin: string;

            /** IntentContext houseKey. */
            public houseKey: string;

            /** IntentContext incarnation. */
            public incarnation: string;

            /** IntentContext sessionId. */
            public sessionId: string;

            /** IntentContext fence. */
            public fence: string;

            /** IntentContext capabilityRevision. */
            public capabilityRevision: string;

            /** IntentContext schemaVersion. */
            public schemaVersion: number;

            /** IntentContext validUntil. */
            public validUntil: (number|Long);

            /**
             * Creates a new IntentContext instance using the specified properties.
             * @param [properties] Properties to set
             * @returns IntentContext instance
             */
            public static create(properties?: popclaw.world.IIntentContext): popclaw.world.IntentContext;

            /**
             * Encodes the specified IntentContext message. Does not implicitly {@link popclaw.world.IntentContext.verify|verify} messages.
             * @param message IntentContext message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IIntentContext, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an IntentContext message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns IntentContext
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.IntentContext;

            /**
             * Creates an IntentContext message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns IntentContext
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.IntentContext;

            /**
             * Creates a plain object from an IntentContext message. Also converts values to other types if specified.
             * @param message IntentContext
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.IntentContext, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this IntentContext to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for IntentContext
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ManifestProof. */
        interface IManifestProof {

            /** ManifestProof house */
            house?: (popclaw.world.IHouseBinding|null);

            /** ManifestProof manifestDigest */
            manifestDigest?: (string|null);

            /** ManifestProof signedAt */
            signedAt?: (number|Long|null);

            /** ManifestProof authoritySignature */
            authoritySignature?: (Uint8Array|null);
        }

        /** Represents a ManifestProof. */
        class ManifestProof implements IManifestProof {

            /**
             * Constructs a new ManifestProof.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IManifestProof);

            /** ManifestProof house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** ManifestProof manifestDigest. */
            public manifestDigest: string;

            /** ManifestProof signedAt. */
            public signedAt: (number|Long);

            /** ManifestProof authoritySignature. */
            public authoritySignature: Uint8Array;

            /**
             * Creates a new ManifestProof instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ManifestProof instance
             */
            public static create(properties?: popclaw.world.IManifestProof): popclaw.world.ManifestProof;

            /**
             * Encodes the specified ManifestProof message. Does not implicitly {@link popclaw.world.ManifestProof.verify|verify} messages.
             * @param message ManifestProof message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IManifestProof, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ManifestProof message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ManifestProof
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ManifestProof;

            /**
             * Creates a ManifestProof message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ManifestProof
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ManifestProof;

            /**
             * Creates a plain object from a ManifestProof message. Also converts values to other types if specified.
             * @param message ManifestProof
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ManifestProof, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ManifestProof to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ManifestProof
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** ActionStatus enum. */
        enum ActionStatus {
            ACTION_UNSPECIFIED = 0,
            ACCEPTED = 1,
            EXECUTING = 2,
            SUCCEEDED = 3,
            REJECTED = 4,
            CANCELLED = 5
        }

        /** Properties of an ActionResult. */
        interface IActionResult {

            /** ActionResult house */
            house?: (popclaw.world.IHouseBinding|null);

            /** ActionResult actorId */
            actorId?: (string|null);

            /** ActionResult audienceId */
            audienceId?: (string|null);

            /** ActionResult requestId */
            requestId?: (string|null);

            /** ActionResult requestDigest */
            requestDigest?: (string|null);

            /** ActionResult executionId */
            executionId?: (string|null);

            /** ActionResult status */
            status?: (popclaw.world.ActionStatus|null);

            /** ActionResult statusRevision */
            statusRevision?: (number|Long|null);

            /** ActionResult code */
            code?: (string|null);

            /** ActionResult kind */
            kind?: (string|null);

            /** ActionResult schemaVersion */
            schemaVersion?: (number|null);

            /** ActionResult capabilityRevision */
            capabilityRevision?: (string|null);

            /** ActionResult resultBody */
            resultBody?: (Uint8Array|null);

            /** ActionResult resultDigest */
            resultDigest?: (string|null);

            /** ActionResult committedAt */
            committedAt?: (number|Long|null);

            /** ActionResult snapshot */
            snapshot?: (popclaw.world.IWorldSnapshot|null);

            /** ActionResult subscription */
            subscription?: (popclaw.world.ISubscriptionDescriptor|null);

            /** ActionResult participation */
            participation?: (popclaw.world.IParticipationDescriptor|null);
        }

        /** Represents an ActionResult. */
        class ActionResult implements IActionResult {

            /**
             * Constructs a new ActionResult.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IActionResult);

            /** ActionResult house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** ActionResult actorId. */
            public actorId: string;

            /** ActionResult audienceId. */
            public audienceId: string;

            /** ActionResult requestId. */
            public requestId: string;

            /** ActionResult requestDigest. */
            public requestDigest: string;

            /** ActionResult executionId. */
            public executionId: string;

            /** ActionResult status. */
            public status: popclaw.world.ActionStatus;

            /** ActionResult statusRevision. */
            public statusRevision: (number|Long);

            /** ActionResult code. */
            public code: string;

            /** ActionResult kind. */
            public kind: string;

            /** ActionResult schemaVersion. */
            public schemaVersion: number;

            /** ActionResult capabilityRevision. */
            public capabilityRevision: string;

            /** ActionResult resultBody. */
            public resultBody: Uint8Array;

            /** ActionResult resultDigest. */
            public resultDigest: string;

            /** ActionResult committedAt. */
            public committedAt: (number|Long);

            /** ActionResult snapshot. */
            public snapshot?: (popclaw.world.IWorldSnapshot|null);

            /** ActionResult subscription. */
            public subscription?: (popclaw.world.ISubscriptionDescriptor|null);

            /** ActionResult participation. */
            public participation?: (popclaw.world.IParticipationDescriptor|null);

            /**
             * Creates a new ActionResult instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ActionResult instance
             */
            public static create(properties?: popclaw.world.IActionResult): popclaw.world.ActionResult;

            /**
             * Encodes the specified ActionResult message. Does not implicitly {@link popclaw.world.ActionResult.verify|verify} messages.
             * @param message ActionResult message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IActionResult, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an ActionResult message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ActionResult
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ActionResult;

            /**
             * Creates an ActionResult message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ActionResult
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ActionResult;

            /**
             * Creates a plain object from an ActionResult message. Also converts values to other types if specified.
             * @param message ActionResult
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ActionResult, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ActionResult to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ActionResult
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SignedActionResult. */
        interface ISignedActionResult {

            /** SignedActionResult result */
            result?: (popclaw.world.IActionResult|null);

            /** SignedActionResult signature */
            signature?: (Uint8Array|null);
        }

        /** Represents a SignedActionResult. */
        class SignedActionResult implements ISignedActionResult {

            /**
             * Constructs a new SignedActionResult.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ISignedActionResult);

            /** SignedActionResult result. */
            public result?: (popclaw.world.IActionResult|null);

            /** SignedActionResult signature. */
            public signature: Uint8Array;

            /**
             * Creates a new SignedActionResult instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SignedActionResult instance
             */
            public static create(properties?: popclaw.world.ISignedActionResult): popclaw.world.SignedActionResult;

            /**
             * Encodes the specified SignedActionResult message. Does not implicitly {@link popclaw.world.SignedActionResult.verify|verify} messages.
             * @param message SignedActionResult message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ISignedActionResult, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SignedActionResult message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SignedActionResult
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.SignedActionResult;

            /**
             * Creates a SignedActionResult message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SignedActionResult
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.SignedActionResult;

            /**
             * Creates a plain object from a SignedActionResult message. Also converts values to other types if specified.
             * @param message SignedActionResult
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.SignedActionResult, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SignedActionResult to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SignedActionResult
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an ActionStatusRequest. */
        interface IActionStatusRequest {

            /** ActionStatusRequest house */
            house?: (popclaw.world.IHouseBinding|null);

            /** ActionStatusRequest actorId */
            actorId?: (string|null);

            /** ActionStatusRequest requestId */
            requestId?: (string|null);

            /** ActionStatusRequest nonce */
            nonce?: (string|null);

            /** ActionStatusRequest issuedAt */
            issuedAt?: (number|Long|null);

            /** ActionStatusRequest expiresAt */
            expiresAt?: (number|Long|null);

            /** ActionStatusRequest signature */
            signature?: (Uint8Array|null);
        }

        /** Represents an ActionStatusRequest. */
        class ActionStatusRequest implements IActionStatusRequest {

            /**
             * Constructs a new ActionStatusRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IActionStatusRequest);

            /** ActionStatusRequest house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** ActionStatusRequest actorId. */
            public actorId: string;

            /** ActionStatusRequest requestId. */
            public requestId: string;

            /** ActionStatusRequest nonce. */
            public nonce: string;

            /** ActionStatusRequest issuedAt. */
            public issuedAt: (number|Long);

            /** ActionStatusRequest expiresAt. */
            public expiresAt: (number|Long);

            /** ActionStatusRequest signature. */
            public signature: Uint8Array;

            /**
             * Creates a new ActionStatusRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ActionStatusRequest instance
             */
            public static create(properties?: popclaw.world.IActionStatusRequest): popclaw.world.ActionStatusRequest;

            /**
             * Encodes the specified ActionStatusRequest message. Does not implicitly {@link popclaw.world.ActionStatusRequest.verify|verify} messages.
             * @param message ActionStatusRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IActionStatusRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an ActionStatusRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ActionStatusRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ActionStatusRequest;

            /**
             * Creates an ActionStatusRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ActionStatusRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ActionStatusRequest;

            /**
             * Creates a plain object from an ActionStatusRequest message. Also converts values to other types if specified.
             * @param message ActionStatusRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ActionStatusRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ActionStatusRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ActionStatusRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an ActionStatusResponse. */
        interface IActionStatusResponse {

            /** ActionStatusResponse result */
            result?: (popclaw.world.ISignedActionResult|null);

            /** ActionStatusResponse progress */
            progress?: (popclaw.world.ISignedSubscriptionObservation|null);
        }

        /** Represents an ActionStatusResponse. */
        class ActionStatusResponse implements IActionStatusResponse {

            /**
             * Constructs a new ActionStatusResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IActionStatusResponse);

            /** ActionStatusResponse result. */
            public result?: (popclaw.world.ISignedActionResult|null);

            /** ActionStatusResponse progress. */
            public progress?: (popclaw.world.ISignedSubscriptionObservation|null);

            /**
             * Creates a new ActionStatusResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ActionStatusResponse instance
             */
            public static create(properties?: popclaw.world.IActionStatusResponse): popclaw.world.ActionStatusResponse;

            /**
             * Encodes the specified ActionStatusResponse message. Does not implicitly {@link popclaw.world.ActionStatusResponse.verify|verify} messages.
             * @param message ActionStatusResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IActionStatusResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an ActionStatusResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ActionStatusResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ActionStatusResponse;

            /**
             * Creates an ActionStatusResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ActionStatusResponse
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ActionStatusResponse;

            /**
             * Creates a plain object from an ActionStatusResponse message. Also converts values to other types if specified.
             * @param message ActionStatusResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ActionStatusResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ActionStatusResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ActionStatusResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SubscriptionObservation. */
        interface ISubscriptionObservation {

            /** SubscriptionObservation version */
            version?: (number|null);

            /** SubscriptionObservation house */
            house?: (popclaw.world.IHouseBinding|null);

            /** SubscriptionObservation actorId */
            actorId?: (string|null);

            /** SubscriptionObservation participationId */
            participationId?: (string|null);

            /** SubscriptionObservation barrierId */
            barrierId?: (string|null);

            /** SubscriptionObservation descriptorRevision */
            descriptorRevision?: (number|Long|null);

            /** SubscriptionObservation observationRevision */
            observationRevision?: (number|Long|null);

            /** SubscriptionObservation publicationState */
            publicationState?: (string|null);

            /** SubscriptionObservation logIncarnation */
            logIncarnation?: (string|null);

            /** SubscriptionObservation highWaterSeq */
            highWaterSeq?: (number|Long|null);

            /** SubscriptionObservation publishedThrough */
            publishedThrough?: (popclaw.world.IScopeThrough[]|null);

            /** SubscriptionObservation queryRequestId */
            queryRequestId?: (string|null);

            /** SubscriptionObservation queryNonce */
            queryNonce?: (string|null);

            /** SubscriptionObservation observedAt */
            observedAt?: (number|Long|null);
        }

        /** Represents a SubscriptionObservation. */
        class SubscriptionObservation implements ISubscriptionObservation {

            /**
             * Constructs a new SubscriptionObservation.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ISubscriptionObservation);

            /** SubscriptionObservation version. */
            public version: number;

            /** SubscriptionObservation house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** SubscriptionObservation actorId. */
            public actorId: string;

            /** SubscriptionObservation participationId. */
            public participationId: string;

            /** SubscriptionObservation barrierId. */
            public barrierId: string;

            /** SubscriptionObservation descriptorRevision. */
            public descriptorRevision: (number|Long);

            /** SubscriptionObservation observationRevision. */
            public observationRevision: (number|Long);

            /** SubscriptionObservation publicationState. */
            public publicationState: string;

            /** SubscriptionObservation logIncarnation. */
            public logIncarnation: string;

            /** SubscriptionObservation highWaterSeq. */
            public highWaterSeq: (number|Long);

            /** SubscriptionObservation publishedThrough. */
            public publishedThrough: popclaw.world.IScopeThrough[];

            /** SubscriptionObservation queryRequestId. */
            public queryRequestId: string;

            /** SubscriptionObservation queryNonce. */
            public queryNonce: string;

            /** SubscriptionObservation observedAt. */
            public observedAt: (number|Long);

            /**
             * Creates a new SubscriptionObservation instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SubscriptionObservation instance
             */
            public static create(properties?: popclaw.world.ISubscriptionObservation): popclaw.world.SubscriptionObservation;

            /**
             * Encodes the specified SubscriptionObservation message. Does not implicitly {@link popclaw.world.SubscriptionObservation.verify|verify} messages.
             * @param message SubscriptionObservation message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ISubscriptionObservation, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SubscriptionObservation message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SubscriptionObservation
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.SubscriptionObservation;

            /**
             * Creates a SubscriptionObservation message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SubscriptionObservation
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.SubscriptionObservation;

            /**
             * Creates a plain object from a SubscriptionObservation message. Also converts values to other types if specified.
             * @param message SubscriptionObservation
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.SubscriptionObservation, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SubscriptionObservation to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SubscriptionObservation
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SignedSubscriptionObservation. */
        interface ISignedSubscriptionObservation {

            /** SignedSubscriptionObservation observation */
            observation?: (popclaw.world.ISubscriptionObservation|null);

            /** SignedSubscriptionObservation signature */
            signature?: (Uint8Array|null);
        }

        /** Represents a SignedSubscriptionObservation. */
        class SignedSubscriptionObservation implements ISignedSubscriptionObservation {

            /**
             * Constructs a new SignedSubscriptionObservation.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ISignedSubscriptionObservation);

            /** SignedSubscriptionObservation observation. */
            public observation?: (popclaw.world.ISubscriptionObservation|null);

            /** SignedSubscriptionObservation signature. */
            public signature: Uint8Array;

            /**
             * Creates a new SignedSubscriptionObservation instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SignedSubscriptionObservation instance
             */
            public static create(properties?: popclaw.world.ISignedSubscriptionObservation): popclaw.world.SignedSubscriptionObservation;

            /**
             * Encodes the specified SignedSubscriptionObservation message. Does not implicitly {@link popclaw.world.SignedSubscriptionObservation.verify|verify} messages.
             * @param message SignedSubscriptionObservation message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ISignedSubscriptionObservation, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SignedSubscriptionObservation message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SignedSubscriptionObservation
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.SignedSubscriptionObservation;

            /**
             * Creates a SignedSubscriptionObservation message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SignedSubscriptionObservation
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.SignedSubscriptionObservation;

            /**
             * Creates a plain object from a SignedSubscriptionObservation message. Also converts values to other types if specified.
             * @param message SignedSubscriptionObservation
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.SignedSubscriptionObservation, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SignedSubscriptionObservation to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SignedSubscriptionObservation
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ScopeThrough. */
        interface IScopeThrough {

            /** ScopeThrough scopeId */
            scopeId?: (string|null);

            /** ScopeThrough throughSeq */
            throughSeq?: (number|Long|null);
        }

        /** Represents a ScopeThrough. */
        class ScopeThrough implements IScopeThrough {

            /**
             * Constructs a new ScopeThrough.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IScopeThrough);

            /** ScopeThrough scopeId. */
            public scopeId: string;

            /** ScopeThrough throughSeq. */
            public throughSeq: (number|Long);

            /**
             * Creates a new ScopeThrough instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ScopeThrough instance
             */
            public static create(properties?: popclaw.world.IScopeThrough): popclaw.world.ScopeThrough;

            /**
             * Encodes the specified ScopeThrough message. Does not implicitly {@link popclaw.world.ScopeThrough.verify|verify} messages.
             * @param message ScopeThrough message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IScopeThrough, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ScopeThrough message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ScopeThrough
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ScopeThrough;

            /**
             * Creates a ScopeThrough message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ScopeThrough
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ScopeThrough;

            /**
             * Creates a plain object from a ScopeThrough message. Also converts values to other types if specified.
             * @param message ScopeThrough
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ScopeThrough, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ScopeThrough to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ScopeThrough
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ParticipationDescriptor. */
        interface IParticipationDescriptor {

            /** ParticipationDescriptor version */
            version?: (number|null);

            /** ParticipationDescriptor house */
            house?: (popclaw.world.IHouseBinding|null);

            /** ParticipationDescriptor actorId */
            actorId?: (string|null);

            /** ParticipationDescriptor participationId */
            participationId?: (string|null);

            /** ParticipationDescriptor revision */
            revision?: (number|Long|null);

            /** ParticipationDescriptor windowId */
            windowId?: (string|null);

            /** ParticipationDescriptor windowOpensAt */
            windowOpensAt?: (number|Long|null);

            /** ParticipationDescriptor windowClosesAt */
            windowClosesAt?: (number|Long|null);

            /** ParticipationDescriptor actionGroups */
            actionGroups?: (popclaw.world.IActionGroup[]|null);

            /** ParticipationDescriptor opportunities */
            opportunities?: (popclaw.world.IOpportunity[]|null);

            /** ParticipationDescriptor budgets */
            budgets?: (popclaw.world.IBudget[]|null);

            /** ParticipationDescriptor dmResponseSlotKey */
            dmResponseSlotKey?: (string|null);
        }

        /** Represents a ParticipationDescriptor. */
        class ParticipationDescriptor implements IParticipationDescriptor {

            /**
             * Constructs a new ParticipationDescriptor.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IParticipationDescriptor);

            /** ParticipationDescriptor version. */
            public version: number;

            /** ParticipationDescriptor house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** ParticipationDescriptor actorId. */
            public actorId: string;

            /** ParticipationDescriptor participationId. */
            public participationId: string;

            /** ParticipationDescriptor revision. */
            public revision: (number|Long);

            /** ParticipationDescriptor windowId. */
            public windowId: string;

            /** ParticipationDescriptor windowOpensAt. */
            public windowOpensAt: (number|Long);

            /** ParticipationDescriptor windowClosesAt. */
            public windowClosesAt: (number|Long);

            /** ParticipationDescriptor actionGroups. */
            public actionGroups: popclaw.world.IActionGroup[];

            /** ParticipationDescriptor opportunities. */
            public opportunities: popclaw.world.IOpportunity[];

            /** ParticipationDescriptor budgets. */
            public budgets: popclaw.world.IBudget[];

            /** ParticipationDescriptor dmResponseSlotKey. */
            public dmResponseSlotKey: string;

            /**
             * Creates a new ParticipationDescriptor instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ParticipationDescriptor instance
             */
            public static create(properties?: popclaw.world.IParticipationDescriptor): popclaw.world.ParticipationDescriptor;

            /**
             * Encodes the specified ParticipationDescriptor message. Does not implicitly {@link popclaw.world.ParticipationDescriptor.verify|verify} messages.
             * @param message ParticipationDescriptor message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IParticipationDescriptor, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ParticipationDescriptor message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ParticipationDescriptor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ParticipationDescriptor;

            /**
             * Creates a ParticipationDescriptor message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ParticipationDescriptor
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ParticipationDescriptor;

            /**
             * Creates a plain object from a ParticipationDescriptor message. Also converts values to other types if specified.
             * @param message ParticipationDescriptor
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ParticipationDescriptor, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ParticipationDescriptor to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ParticipationDescriptor
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an ActionGroup. */
        interface IActionGroup {

            /** ActionGroup id */
            id?: (string|null);

            /** ActionGroup intentKinds */
            intentKinds?: (string[]|null);

            /** ActionGroup controlReset */
            controlReset?: (string|null);

            /** ActionGroup channels */
            channels?: (string[]|null);
        }

        /** Represents an ActionGroup. */
        class ActionGroup implements IActionGroup {

            /**
             * Constructs a new ActionGroup.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IActionGroup);

            /** ActionGroup id. */
            public id: string;

            /** ActionGroup intentKinds. */
            public intentKinds: string[];

            /** ActionGroup controlReset. */
            public controlReset: string;

            /** ActionGroup channels. */
            public channels: string[];

            /**
             * Creates a new ActionGroup instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ActionGroup instance
             */
            public static create(properties?: popclaw.world.IActionGroup): popclaw.world.ActionGroup;

            /**
             * Encodes the specified ActionGroup message. Does not implicitly {@link popclaw.world.ActionGroup.verify|verify} messages.
             * @param message ActionGroup message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IActionGroup, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an ActionGroup message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ActionGroup
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ActionGroup;

            /**
             * Creates an ActionGroup message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ActionGroup
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ActionGroup;

            /**
             * Creates a plain object from an ActionGroup message. Also converts values to other types if specified.
             * @param message ActionGroup
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ActionGroup, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ActionGroup to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ActionGroup
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an Opportunity. */
        interface IOpportunity {

            /** Opportunity id */
            id?: (string|null);

            /** Opportunity sourceEventId */
            sourceEventId?: (string|null);

            /** Opportunity actionGroupId */
            actionGroupId?: (string|null);

            /** Opportunity budgetGroupId */
            budgetGroupId?: (string|null);

            /** Opportunity budgetWindowId */
            budgetWindowId?: (string|null);

            /** Opportunity notBefore */
            notBefore?: (number|Long|null);

            /** Opportunity expiresAt */
            expiresAt?: (number|Long|null);

            /** Opportunity dedupeKey */
            dedupeKey?: (string|null);

            /** Opportunity channels */
            channels?: (string[]|null);
        }

        /** Represents an Opportunity. */
        class Opportunity implements IOpportunity {

            /**
             * Constructs a new Opportunity.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IOpportunity);

            /** Opportunity id. */
            public id: string;

            /** Opportunity sourceEventId. */
            public sourceEventId: string;

            /** Opportunity actionGroupId. */
            public actionGroupId: string;

            /** Opportunity budgetGroupId. */
            public budgetGroupId: string;

            /** Opportunity budgetWindowId. */
            public budgetWindowId: string;

            /** Opportunity notBefore. */
            public notBefore: (number|Long);

            /** Opportunity expiresAt. */
            public expiresAt: (number|Long);

            /** Opportunity dedupeKey. */
            public dedupeKey: string;

            /** Opportunity channels. */
            public channels: string[];

            /**
             * Creates a new Opportunity instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Opportunity instance
             */
            public static create(properties?: popclaw.world.IOpportunity): popclaw.world.Opportunity;

            /**
             * Encodes the specified Opportunity message. Does not implicitly {@link popclaw.world.Opportunity.verify|verify} messages.
             * @param message Opportunity message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IOpportunity, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an Opportunity message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns Opportunity
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.Opportunity;

            /**
             * Creates an Opportunity message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Opportunity
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.Opportunity;

            /**
             * Creates a plain object from an Opportunity message. Also converts values to other types if specified.
             * @param message Opportunity
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.Opportunity, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Opportunity to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for Opportunity
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a Budget. */
        interface IBudget {

            /** Budget id */
            id?: (string|null);

            /** Budget windowId */
            windowId?: (string|null);

            /** Budget resource */
            resource?: (string|null);

            /** Budget suggestedLimit */
            suggestedLimit?: (number|null);
        }

        /** Represents a Budget. */
        class Budget implements IBudget {

            /**
             * Constructs a new Budget.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IBudget);

            /** Budget id. */
            public id: string;

            /** Budget windowId. */
            public windowId: string;

            /** Budget resource. */
            public resource: string;

            /** Budget suggestedLimit. */
            public suggestedLimit: number;

            /**
             * Creates a new Budget instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Budget instance
             */
            public static create(properties?: popclaw.world.IBudget): popclaw.world.Budget;

            /**
             * Encodes the specified Budget message. Does not implicitly {@link popclaw.world.Budget.verify|verify} messages.
             * @param message Budget message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IBudget, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Budget message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns Budget
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.Budget;

            /**
             * Creates a Budget message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Budget
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.Budget;

            /**
             * Creates a plain object from a Budget message. Also converts values to other types if specified.
             * @param message Budget
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.Budget, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Budget to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for Budget
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a WorldStreamBoundary. */
        interface IWorldStreamBoundary {

            /** WorldStreamBoundary logIncarnation */
            logIncarnation?: (string|null);

            /** WorldStreamBoundary scopes */
            scopes?: (string[]|null);

            /** WorldStreamBoundary highWaterSeq */
            highWaterSeq?: (number|Long|null);
        }

        /** Represents a WorldStreamBoundary. */
        class WorldStreamBoundary implements IWorldStreamBoundary {

            /**
             * Constructs a new WorldStreamBoundary.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IWorldStreamBoundary);

            /** WorldStreamBoundary logIncarnation. */
            public logIncarnation: string;

            /** WorldStreamBoundary scopes. */
            public scopes: string[];

            /** WorldStreamBoundary highWaterSeq. */
            public highWaterSeq: (number|Long);

            /**
             * Creates a new WorldStreamBoundary instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WorldStreamBoundary instance
             */
            public static create(properties?: popclaw.world.IWorldStreamBoundary): popclaw.world.WorldStreamBoundary;

            /**
             * Encodes the specified WorldStreamBoundary message. Does not implicitly {@link popclaw.world.WorldStreamBoundary.verify|verify} messages.
             * @param message WorldStreamBoundary message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IWorldStreamBoundary, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WorldStreamBoundary message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WorldStreamBoundary
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.WorldStreamBoundary;

            /**
             * Creates a WorldStreamBoundary message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WorldStreamBoundary
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.WorldStreamBoundary;

            /**
             * Creates a plain object from a WorldStreamBoundary message. Also converts values to other types if specified.
             * @param message WorldStreamBoundary
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.WorldStreamBoundary, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WorldStreamBoundary to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WorldStreamBoundary
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a WorldStreamCheckpoint. */
        interface IWorldStreamCheckpoint {

            /** WorldStreamCheckpoint phase */
            phase?: (string|null);

            /** WorldStreamCheckpoint scopes */
            scopes?: (popclaw.world.IScopeThrough[]|null);
        }

        /** Represents a WorldStreamCheckpoint. */
        class WorldStreamCheckpoint implements IWorldStreamCheckpoint {

            /**
             * Constructs a new WorldStreamCheckpoint.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IWorldStreamCheckpoint);

            /** WorldStreamCheckpoint phase. */
            public phase: string;

            /** WorldStreamCheckpoint scopes. */
            public scopes: popclaw.world.IScopeThrough[];

            /**
             * Creates a new WorldStreamCheckpoint instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WorldStreamCheckpoint instance
             */
            public static create(properties?: popclaw.world.IWorldStreamCheckpoint): popclaw.world.WorldStreamCheckpoint;

            /**
             * Encodes the specified WorldStreamCheckpoint message. Does not implicitly {@link popclaw.world.WorldStreamCheckpoint.verify|verify} messages.
             * @param message WorldStreamCheckpoint message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IWorldStreamCheckpoint, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WorldStreamCheckpoint message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WorldStreamCheckpoint
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.WorldStreamCheckpoint;

            /**
             * Creates a WorldStreamCheckpoint message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WorldStreamCheckpoint
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.WorldStreamCheckpoint;

            /**
             * Creates a plain object from a WorldStreamCheckpoint message. Also converts values to other types if specified.
             * @param message WorldStreamCheckpoint
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.WorldStreamCheckpoint, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WorldStreamCheckpoint to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WorldStreamCheckpoint
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a WorldStreamGap. */
        interface IWorldStreamGap {

            /** WorldStreamGap reason */
            reason?: (string|null);

            /** WorldStreamGap scopeId */
            scopeId?: (string|null);

            /** WorldStreamGap boundary */
            boundary?: (popclaw.world.IWorldStreamBoundary|null);
        }

        /** Represents a WorldStreamGap. */
        class WorldStreamGap implements IWorldStreamGap {

            /**
             * Constructs a new WorldStreamGap.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IWorldStreamGap);

            /** WorldStreamGap reason. */
            public reason: string;

            /** WorldStreamGap scopeId. */
            public scopeId: string;

            /** WorldStreamGap boundary. */
            public boundary?: (popclaw.world.IWorldStreamBoundary|null);

            /**
             * Creates a new WorldStreamGap instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WorldStreamGap instance
             */
            public static create(properties?: popclaw.world.IWorldStreamGap): popclaw.world.WorldStreamGap;

            /**
             * Encodes the specified WorldStreamGap message. Does not implicitly {@link popclaw.world.WorldStreamGap.verify|verify} messages.
             * @param message WorldStreamGap message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IWorldStreamGap, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WorldStreamGap message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WorldStreamGap
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.WorldStreamGap;

            /**
             * Creates a WorldStreamGap message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WorldStreamGap
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.WorldStreamGap;

            /**
             * Creates a plain object from a WorldStreamGap message. Also converts values to other types if specified.
             * @param message WorldStreamGap
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.WorldStreamGap, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WorldStreamGap to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WorldStreamGap
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ScopeCursor. */
        interface IScopeCursor {

            /** ScopeCursor scopeId */
            scopeId?: (string|null);

            /** ScopeCursor afterSeq */
            afterSeq?: (number|Long|null);
        }

        /** Represents a ScopeCursor. */
        class ScopeCursor implements IScopeCursor {

            /**
             * Constructs a new ScopeCursor.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IScopeCursor);

            /** ScopeCursor scopeId. */
            public scopeId: string;

            /** ScopeCursor afterSeq. */
            public afterSeq: (number|Long);

            /**
             * Creates a new ScopeCursor instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ScopeCursor instance
             */
            public static create(properties?: popclaw.world.IScopeCursor): popclaw.world.ScopeCursor;

            /**
             * Encodes the specified ScopeCursor message. Does not implicitly {@link popclaw.world.ScopeCursor.verify|verify} messages.
             * @param message ScopeCursor message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IScopeCursor, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ScopeCursor message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ScopeCursor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ScopeCursor;

            /**
             * Creates a ScopeCursor message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ScopeCursor
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ScopeCursor;

            /**
             * Creates a plain object from a ScopeCursor message. Also converts values to other types if specified.
             * @param message ScopeCursor
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ScopeCursor, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ScopeCursor to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ScopeCursor
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SubscriptionDescriptor. */
        interface ISubscriptionDescriptor {

            /** SubscriptionDescriptor house */
            house?: (popclaw.world.IHouseBinding|null);

            /** SubscriptionDescriptor actorId */
            actorId?: (string|null);

            /** SubscriptionDescriptor participationId */
            participationId?: (string|null);

            /** SubscriptionDescriptor descriptorRevision */
            descriptorRevision?: (number|Long|null);

            /** SubscriptionDescriptor logIncarnation */
            logIncarnation?: (string|null);

            /** SubscriptionDescriptor scopes */
            scopes?: (string[]|null);

            /** SubscriptionDescriptor barrierId */
            barrierId?: (string|null);
        }

        /** Represents a SubscriptionDescriptor. */
        class SubscriptionDescriptor implements ISubscriptionDescriptor {

            /**
             * Constructs a new SubscriptionDescriptor.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ISubscriptionDescriptor);

            /** SubscriptionDescriptor house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** SubscriptionDescriptor actorId. */
            public actorId: string;

            /** SubscriptionDescriptor participationId. */
            public participationId: string;

            /** SubscriptionDescriptor descriptorRevision. */
            public descriptorRevision: (number|Long);

            /** SubscriptionDescriptor logIncarnation. */
            public logIncarnation: string;

            /** SubscriptionDescriptor scopes. */
            public scopes: string[];

            /** SubscriptionDescriptor barrierId. */
            public barrierId: string;

            /**
             * Creates a new SubscriptionDescriptor instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SubscriptionDescriptor instance
             */
            public static create(properties?: popclaw.world.ISubscriptionDescriptor): popclaw.world.SubscriptionDescriptor;

            /**
             * Encodes the specified SubscriptionDescriptor message. Does not implicitly {@link popclaw.world.SubscriptionDescriptor.verify|verify} messages.
             * @param message SubscriptionDescriptor message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ISubscriptionDescriptor, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SubscriptionDescriptor message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SubscriptionDescriptor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.SubscriptionDescriptor;

            /**
             * Creates a SubscriptionDescriptor message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SubscriptionDescriptor
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.SubscriptionDescriptor;

            /**
             * Creates a plain object from a SubscriptionDescriptor message. Also converts values to other types if specified.
             * @param message SubscriptionDescriptor
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.SubscriptionDescriptor, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SubscriptionDescriptor to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SubscriptionDescriptor
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a WorldSnapshot. */
        interface IWorldSnapshot {

            /** WorldSnapshot stateRef */
            stateRef?: (string|null);

            /** WorldSnapshot stateRevision */
            stateRevision?: (number|Long|null);

            /** WorldSnapshot asOf */
            asOf?: (number|Long|null);

            /** WorldSnapshot schemaKind */
            schemaKind?: (string|null);

            /** WorldSnapshot schemaVersion */
            schemaVersion?: (number|null);

            /** WorldSnapshot body */
            body?: (Uint8Array|null);
        }

        /** Represents a WorldSnapshot. */
        class WorldSnapshot implements IWorldSnapshot {

            /**
             * Constructs a new WorldSnapshot.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IWorldSnapshot);

            /** WorldSnapshot stateRef. */
            public stateRef: string;

            /** WorldSnapshot stateRevision. */
            public stateRevision: (number|Long);

            /** WorldSnapshot asOf. */
            public asOf: (number|Long);

            /** WorldSnapshot schemaKind. */
            public schemaKind: string;

            /** WorldSnapshot schemaVersion. */
            public schemaVersion: number;

            /** WorldSnapshot body. */
            public body: Uint8Array;

            /**
             * Creates a new WorldSnapshot instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WorldSnapshot instance
             */
            public static create(properties?: popclaw.world.IWorldSnapshot): popclaw.world.WorldSnapshot;

            /**
             * Encodes the specified WorldSnapshot message. Does not implicitly {@link popclaw.world.WorldSnapshot.verify|verify} messages.
             * @param message WorldSnapshot message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IWorldSnapshot, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WorldSnapshot message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WorldSnapshot
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.WorldSnapshot;

            /**
             * Creates a WorldSnapshot message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WorldSnapshot
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.WorldSnapshot;

            /**
             * Creates a plain object from a WorldSnapshot message. Also converts values to other types if specified.
             * @param message WorldSnapshot
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.WorldSnapshot, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WorldSnapshot to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WorldSnapshot
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SubscriptionBarrier. */
        interface ISubscriptionBarrier {

            /** SubscriptionBarrier barrierId */
            barrierId?: (string|null);

            /** SubscriptionBarrier house */
            house?: (popclaw.world.IHouseBinding|null);

            /** SubscriptionBarrier actorId */
            actorId?: (string|null);

            /** SubscriptionBarrier participationId */
            participationId?: (string|null);

            /** SubscriptionBarrier stateRef */
            stateRef?: (string|null);

            /** SubscriptionBarrier stateRevision */
            stateRevision?: (number|Long|null);

            /** SubscriptionBarrier scopes */
            scopes?: (string[]|null);

            /** SubscriptionBarrier members */
            members?: (popclaw.world.IBarrierMember[]|null);

            /** SubscriptionBarrier membersDigest */
            membersDigest?: (string|null);

            /** SubscriptionBarrier createdAt */
            createdAt?: (number|Long|null);

            /** SubscriptionBarrier memberTotal */
            memberTotal?: (number|Long|null);
        }

        /** Represents a SubscriptionBarrier. */
        class SubscriptionBarrier implements ISubscriptionBarrier {

            /**
             * Constructs a new SubscriptionBarrier.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ISubscriptionBarrier);

            /** SubscriptionBarrier barrierId. */
            public barrierId: string;

            /** SubscriptionBarrier house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** SubscriptionBarrier actorId. */
            public actorId: string;

            /** SubscriptionBarrier participationId. */
            public participationId: string;

            /** SubscriptionBarrier stateRef. */
            public stateRef: string;

            /** SubscriptionBarrier stateRevision. */
            public stateRevision: (number|Long);

            /** SubscriptionBarrier scopes. */
            public scopes: string[];

            /** SubscriptionBarrier members. */
            public members: popclaw.world.IBarrierMember[];

            /** SubscriptionBarrier membersDigest. */
            public membersDigest: string;

            /** SubscriptionBarrier createdAt. */
            public createdAt: (number|Long);

            /** SubscriptionBarrier memberTotal. */
            public memberTotal: (number|Long);

            /**
             * Creates a new SubscriptionBarrier instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SubscriptionBarrier instance
             */
            public static create(properties?: popclaw.world.ISubscriptionBarrier): popclaw.world.SubscriptionBarrier;

            /**
             * Encodes the specified SubscriptionBarrier message. Does not implicitly {@link popclaw.world.SubscriptionBarrier.verify|verify} messages.
             * @param message SubscriptionBarrier message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ISubscriptionBarrier, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SubscriptionBarrier message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SubscriptionBarrier
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.SubscriptionBarrier;

            /**
             * Creates a SubscriptionBarrier message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SubscriptionBarrier
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.SubscriptionBarrier;

            /**
             * Creates a plain object from a SubscriptionBarrier message. Also converts values to other types if specified.
             * @param message SubscriptionBarrier
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.SubscriptionBarrier, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SubscriptionBarrier to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SubscriptionBarrier
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a BarrierMember. */
        interface IBarrierMember {

            /** BarrierMember eventId */
            eventId?: (string|null);

            /** BarrierMember kind */
            kind?: (string|null);

            /** BarrierMember scopes */
            scopes?: (string[]|null);
        }

        /** Represents a BarrierMember. */
        class BarrierMember implements IBarrierMember {

            /**
             * Constructs a new BarrierMember.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IBarrierMember);

            /** BarrierMember eventId. */
            public eventId: string;

            /** BarrierMember kind. */
            public kind: string;

            /** BarrierMember scopes. */
            public scopes: string[];

            /**
             * Creates a new BarrierMember instance using the specified properties.
             * @param [properties] Properties to set
             * @returns BarrierMember instance
             */
            public static create(properties?: popclaw.world.IBarrierMember): popclaw.world.BarrierMember;

            /**
             * Encodes the specified BarrierMember message. Does not implicitly {@link popclaw.world.BarrierMember.verify|verify} messages.
             * @param message BarrierMember message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IBarrierMember, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a BarrierMember message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns BarrierMember
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.BarrierMember;

            /**
             * Creates a BarrierMember message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns BarrierMember
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.BarrierMember;

            /**
             * Creates a plain object from a BarrierMember message. Also converts values to other types if specified.
             * @param message BarrierMember
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.BarrierMember, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this BarrierMember to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for BarrierMember
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a PublicationReceipt. */
        interface IPublicationReceipt {

            /** PublicationReceipt eventId */
            eventId?: (string|null);

            /** PublicationReceipt seq */
            seq?: (number|Long|null);

            /** PublicationReceipt logIncarnation */
            logIncarnation?: (string|null);

            /** PublicationReceipt scopes */
            scopes?: (string[]|null);

            /** PublicationReceipt logged */
            logged?: (boolean|null);
        }

        /** Represents a PublicationReceipt. */
        class PublicationReceipt implements IPublicationReceipt {

            /**
             * Constructs a new PublicationReceipt.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IPublicationReceipt);

            /** PublicationReceipt eventId. */
            public eventId: string;

            /** PublicationReceipt seq. */
            public seq: (number|Long);

            /** PublicationReceipt logIncarnation. */
            public logIncarnation: string;

            /** PublicationReceipt scopes. */
            public scopes: string[];

            /** PublicationReceipt logged. */
            public logged: boolean;

            /**
             * Creates a new PublicationReceipt instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PublicationReceipt instance
             */
            public static create(properties?: popclaw.world.IPublicationReceipt): popclaw.world.PublicationReceipt;

            /**
             * Encodes the specified PublicationReceipt message. Does not implicitly {@link popclaw.world.PublicationReceipt.verify|verify} messages.
             * @param message PublicationReceipt message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IPublicationReceipt, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PublicationReceipt message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PublicationReceipt
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.PublicationReceipt;

            /**
             * Creates a PublicationReceipt message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PublicationReceipt
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.PublicationReceipt;

            /**
             * Creates a plain object from a PublicationReceipt message. Also converts values to other types if specified.
             * @param message PublicationReceipt
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.PublicationReceipt, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PublicationReceipt to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PublicationReceipt
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SubscriptionReadiness. */
        interface ISubscriptionReadiness {

            /** SubscriptionReadiness barrierId */
            barrierId?: (string|null);

            /** SubscriptionReadiness publicationState */
            publicationState?: (string|null);

            /** SubscriptionReadiness detailCode */
            detailCode?: (string|null);

            /** SubscriptionReadiness readinessRevision */
            readinessRevision?: (number|Long|null);

            /** SubscriptionReadiness receipts */
            receipts?: (popclaw.world.IPublicationReceipt[]|null);

            /** SubscriptionReadiness updatedAt */
            updatedAt?: (number|Long|null);
        }

        /** Represents a SubscriptionReadiness. */
        class SubscriptionReadiness implements ISubscriptionReadiness {

            /**
             * Constructs a new SubscriptionReadiness.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ISubscriptionReadiness);

            /** SubscriptionReadiness barrierId. */
            public barrierId: string;

            /** SubscriptionReadiness publicationState. */
            public publicationState: string;

            /** SubscriptionReadiness detailCode. */
            public detailCode: string;

            /** SubscriptionReadiness readinessRevision. */
            public readinessRevision: (number|Long);

            /** SubscriptionReadiness receipts. */
            public receipts: popclaw.world.IPublicationReceipt[];

            /** SubscriptionReadiness updatedAt. */
            public updatedAt: (number|Long);

            /**
             * Creates a new SubscriptionReadiness instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SubscriptionReadiness instance
             */
            public static create(properties?: popclaw.world.ISubscriptionReadiness): popclaw.world.SubscriptionReadiness;

            /**
             * Encodes the specified SubscriptionReadiness message. Does not implicitly {@link popclaw.world.SubscriptionReadiness.verify|verify} messages.
             * @param message SubscriptionReadiness message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ISubscriptionReadiness, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SubscriptionReadiness message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SubscriptionReadiness
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.SubscriptionReadiness;

            /**
             * Creates a SubscriptionReadiness message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SubscriptionReadiness
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.SubscriptionReadiness;

            /**
             * Creates a plain object from a SubscriptionReadiness message. Also converts values to other types if specified.
             * @param message SubscriptionReadiness
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.SubscriptionReadiness, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SubscriptionReadiness to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SubscriptionReadiness
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ClaimActionsRequest. */
        interface IClaimActionsRequest {

            /** ClaimActionsRequest workerId */
            workerId?: (string|null);

            /** ClaimActionsRequest house */
            house?: (popclaw.world.IHouseBinding|null);

            /** ClaimActionsRequest kinds */
            kinds?: (string[]|null);

            /** ClaimActionsRequest maxCount */
            maxCount?: (number|null);

            /** ClaimActionsRequest maxSchemaVersion */
            maxSchemaVersion?: (number|null);
        }

        /** Represents a ClaimActionsRequest. */
        class ClaimActionsRequest implements IClaimActionsRequest {

            /**
             * Constructs a new ClaimActionsRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IClaimActionsRequest);

            /** ClaimActionsRequest workerId. */
            public workerId: string;

            /** ClaimActionsRequest house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** ClaimActionsRequest kinds. */
            public kinds: string[];

            /** ClaimActionsRequest maxCount. */
            public maxCount: number;

            /** ClaimActionsRequest maxSchemaVersion. */
            public maxSchemaVersion: number;

            /**
             * Creates a new ClaimActionsRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ClaimActionsRequest instance
             */
            public static create(properties?: popclaw.world.IClaimActionsRequest): popclaw.world.ClaimActionsRequest;

            /**
             * Encodes the specified ClaimActionsRequest message. Does not implicitly {@link popclaw.world.ClaimActionsRequest.verify|verify} messages.
             * @param message ClaimActionsRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IClaimActionsRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ClaimActionsRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ClaimActionsRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ClaimActionsRequest;

            /**
             * Creates a ClaimActionsRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ClaimActionsRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ClaimActionsRequest;

            /**
             * Creates a plain object from a ClaimActionsRequest message. Also converts values to other types if specified.
             * @param message ClaimActionsRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ClaimActionsRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ClaimActionsRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ClaimActionsRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ClaimActionsResponse. */
        interface IClaimActionsResponse {

            /** ClaimActionsResponse permits */
            permits?: (popclaw.world.ISignedExecutionPermit[]|null);

            /** ClaimActionsResponse requestEnvelopes */
            requestEnvelopes?: (Uint8Array[]|null);
        }

        /** Represents a ClaimActionsResponse. */
        class ClaimActionsResponse implements IClaimActionsResponse {

            /**
             * Constructs a new ClaimActionsResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IClaimActionsResponse);

            /** ClaimActionsResponse permits. */
            public permits: popclaw.world.ISignedExecutionPermit[];

            /** ClaimActionsResponse requestEnvelopes. */
            public requestEnvelopes: Uint8Array[];

            /**
             * Creates a new ClaimActionsResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ClaimActionsResponse instance
             */
            public static create(properties?: popclaw.world.IClaimActionsResponse): popclaw.world.ClaimActionsResponse;

            /**
             * Encodes the specified ClaimActionsResponse message. Does not implicitly {@link popclaw.world.ClaimActionsResponse.verify|verify} messages.
             * @param message ClaimActionsResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IClaimActionsResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ClaimActionsResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ClaimActionsResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ClaimActionsResponse;

            /**
             * Creates a ClaimActionsResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ClaimActionsResponse
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ClaimActionsResponse;

            /**
             * Creates a plain object from a ClaimActionsResponse message. Also converts values to other types if specified.
             * @param message ClaimActionsResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ClaimActionsResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ClaimActionsResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ClaimActionsResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an ExecutionPermit. */
        interface IExecutionPermit {

            /** ExecutionPermit executionId */
            executionId?: (string|null);

            /** ExecutionPermit requestId */
            requestId?: (string|null);

            /** ExecutionPermit requestDigest */
            requestDigest?: (string|null);

            /** ExecutionPermit house */
            house?: (popclaw.world.IHouseBinding|null);

            /** ExecutionPermit actorId */
            actorId?: (string|null);

            /** ExecutionPermit audienceId */
            audienceId?: (string|null);

            /** ExecutionPermit sessionId */
            sessionId?: (string|null);

            /** ExecutionPermit fence */
            fence?: (string|null);

            /** ExecutionPermit workerId */
            workerId?: (string|null);

            /** ExecutionPermit kind */
            kind?: (string|null);

            /** ExecutionPermit schemaVersion */
            schemaVersion?: (number|null);

            /** ExecutionPermit capabilityRevision */
            capabilityRevision?: (string|null);

            /** ExecutionPermit paramsDigest */
            paramsDigest?: (string|null);

            /** ExecutionPermit validUntil */
            validUntil?: (number|Long|null);

            /** ExecutionPermit grantedAt */
            grantedAt?: (number|Long|null);
        }

        /** Represents an ExecutionPermit. */
        class ExecutionPermit implements IExecutionPermit {

            /**
             * Constructs a new ExecutionPermit.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IExecutionPermit);

            /** ExecutionPermit executionId. */
            public executionId: string;

            /** ExecutionPermit requestId. */
            public requestId: string;

            /** ExecutionPermit requestDigest. */
            public requestDigest: string;

            /** ExecutionPermit house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** ExecutionPermit actorId. */
            public actorId: string;

            /** ExecutionPermit audienceId. */
            public audienceId: string;

            /** ExecutionPermit sessionId. */
            public sessionId: string;

            /** ExecutionPermit fence. */
            public fence: string;

            /** ExecutionPermit workerId. */
            public workerId: string;

            /** ExecutionPermit kind. */
            public kind: string;

            /** ExecutionPermit schemaVersion. */
            public schemaVersion: number;

            /** ExecutionPermit capabilityRevision. */
            public capabilityRevision: string;

            /** ExecutionPermit paramsDigest. */
            public paramsDigest: string;

            /** ExecutionPermit validUntil. */
            public validUntil: (number|Long);

            /** ExecutionPermit grantedAt. */
            public grantedAt: (number|Long);

            /**
             * Creates a new ExecutionPermit instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ExecutionPermit instance
             */
            public static create(properties?: popclaw.world.IExecutionPermit): popclaw.world.ExecutionPermit;

            /**
             * Encodes the specified ExecutionPermit message. Does not implicitly {@link popclaw.world.ExecutionPermit.verify|verify} messages.
             * @param message ExecutionPermit message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IExecutionPermit, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an ExecutionPermit message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ExecutionPermit
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ExecutionPermit;

            /**
             * Creates an ExecutionPermit message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ExecutionPermit
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ExecutionPermit;

            /**
             * Creates a plain object from an ExecutionPermit message. Also converts values to other types if specified.
             * @param message ExecutionPermit
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ExecutionPermit, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ExecutionPermit to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ExecutionPermit
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SignedExecutionPermit. */
        interface ISignedExecutionPermit {

            /** SignedExecutionPermit permit */
            permit?: (popclaw.world.IExecutionPermit|null);

            /** SignedExecutionPermit signature */
            signature?: (Uint8Array|null);
        }

        /** Represents a SignedExecutionPermit. */
        class SignedExecutionPermit implements ISignedExecutionPermit {

            /**
             * Constructs a new SignedExecutionPermit.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ISignedExecutionPermit);

            /** SignedExecutionPermit permit. */
            public permit?: (popclaw.world.IExecutionPermit|null);

            /** SignedExecutionPermit signature. */
            public signature: Uint8Array;

            /**
             * Creates a new SignedExecutionPermit instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SignedExecutionPermit instance
             */
            public static create(properties?: popclaw.world.ISignedExecutionPermit): popclaw.world.SignedExecutionPermit;

            /**
             * Encodes the specified SignedExecutionPermit message. Does not implicitly {@link popclaw.world.SignedExecutionPermit.verify|verify} messages.
             * @param message SignedExecutionPermit message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ISignedExecutionPermit, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SignedExecutionPermit message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SignedExecutionPermit
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.SignedExecutionPermit;

            /**
             * Creates a SignedExecutionPermit message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SignedExecutionPermit
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.SignedExecutionPermit;

            /**
             * Creates a plain object from a SignedExecutionPermit message. Also converts values to other types if specified.
             * @param message SignedExecutionPermit
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.SignedExecutionPermit, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SignedExecutionPermit to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SignedExecutionPermit
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a WorkerResult. */
        interface IWorkerResult {

            /** WorkerResult executionId */
            executionId?: (string|null);

            /** WorkerResult requestId */
            requestId?: (string|null);

            /** WorkerResult requestDigest */
            requestDigest?: (string|null);

            /** WorkerResult workerId */
            workerId?: (string|null);

            /** WorkerResult house */
            house?: (popclaw.world.IHouseBinding|null);

            /** WorkerResult status */
            status?: (string|null);

            /** WorkerResult code */
            code?: (string|null);

            /** WorkerResult resultBody */
            resultBody?: (Uint8Array|null);

            /** WorkerResult resultDigest */
            resultDigest?: (string|null);

            /** WorkerResult businessRevision */
            businessRevision?: (string|null);

            /** WorkerResult committedAt */
            committedAt?: (number|Long|null);

            /** WorkerResult snapshot */
            snapshot?: (popclaw.world.IWorldSnapshot|null);

            /** WorkerResult subscription */
            subscription?: (popclaw.world.ISubscriptionDescriptor|null);

            /** WorkerResult participation */
            participation?: (popclaw.world.IParticipationDescriptor|null);
        }

        /** Represents a WorkerResult. */
        class WorkerResult implements IWorkerResult {

            /**
             * Constructs a new WorkerResult.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IWorkerResult);

            /** WorkerResult executionId. */
            public executionId: string;

            /** WorkerResult requestId. */
            public requestId: string;

            /** WorkerResult requestDigest. */
            public requestDigest: string;

            /** WorkerResult workerId. */
            public workerId: string;

            /** WorkerResult house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** WorkerResult status. */
            public status: string;

            /** WorkerResult code. */
            public code: string;

            /** WorkerResult resultBody. */
            public resultBody: Uint8Array;

            /** WorkerResult resultDigest. */
            public resultDigest: string;

            /** WorkerResult businessRevision. */
            public businessRevision: string;

            /** WorkerResult committedAt. */
            public committedAt: (number|Long);

            /** WorkerResult snapshot. */
            public snapshot?: (popclaw.world.IWorldSnapshot|null);

            /** WorkerResult subscription. */
            public subscription?: (popclaw.world.ISubscriptionDescriptor|null);

            /** WorkerResult participation. */
            public participation?: (popclaw.world.IParticipationDescriptor|null);

            /**
             * Creates a new WorkerResult instance using the specified properties.
             * @param [properties] Properties to set
             * @returns WorkerResult instance
             */
            public static create(properties?: popclaw.world.IWorkerResult): popclaw.world.WorkerResult;

            /**
             * Encodes the specified WorkerResult message. Does not implicitly {@link popclaw.world.WorkerResult.verify|verify} messages.
             * @param message WorkerResult message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IWorkerResult, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a WorkerResult message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns WorkerResult
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.WorkerResult;

            /**
             * Creates a WorkerResult message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns WorkerResult
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.WorkerResult;

            /**
             * Creates a plain object from a WorkerResult message. Also converts values to other types if specified.
             * @param message WorkerResult
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.WorkerResult, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this WorkerResult to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for WorkerResult
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SignedWorkerResult. */
        interface ISignedWorkerResult {

            /** SignedWorkerResult result */
            result?: (popclaw.world.IWorkerResult|null);

            /** SignedWorkerResult signature */
            signature?: (Uint8Array|null);
        }

        /** Represents a SignedWorkerResult. */
        class SignedWorkerResult implements ISignedWorkerResult {

            /**
             * Constructs a new SignedWorkerResult.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ISignedWorkerResult);

            /** SignedWorkerResult result. */
            public result?: (popclaw.world.IWorkerResult|null);

            /** SignedWorkerResult signature. */
            public signature: Uint8Array;

            /**
             * Creates a new SignedWorkerResult instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SignedWorkerResult instance
             */
            public static create(properties?: popclaw.world.ISignedWorkerResult): popclaw.world.SignedWorkerResult;

            /**
             * Encodes the specified SignedWorkerResult message. Does not implicitly {@link popclaw.world.SignedWorkerResult.verify|verify} messages.
             * @param message SignedWorkerResult message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ISignedWorkerResult, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SignedWorkerResult message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SignedWorkerResult
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.SignedWorkerResult;

            /**
             * Creates a SignedWorkerResult message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SignedWorkerResult
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.SignedWorkerResult;

            /**
             * Creates a plain object from a SignedWorkerResult message. Also converts values to other types if specified.
             * @param message SignedWorkerResult
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.SignedWorkerResult, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SignedWorkerResult to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SignedWorkerResult
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a CompleteActionsRequest. */
        interface ICompleteActionsRequest {

            /** CompleteActionsRequest results */
            results?: (popclaw.world.ISignedWorkerResult[]|null);
        }

        /** Represents a CompleteActionsRequest. */
        class CompleteActionsRequest implements ICompleteActionsRequest {

            /**
             * Constructs a new CompleteActionsRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ICompleteActionsRequest);

            /** CompleteActionsRequest results. */
            public results: popclaw.world.ISignedWorkerResult[];

            /**
             * Creates a new CompleteActionsRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns CompleteActionsRequest instance
             */
            public static create(properties?: popclaw.world.ICompleteActionsRequest): popclaw.world.CompleteActionsRequest;

            /**
             * Encodes the specified CompleteActionsRequest message. Does not implicitly {@link popclaw.world.CompleteActionsRequest.verify|verify} messages.
             * @param message CompleteActionsRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ICompleteActionsRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a CompleteActionsRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns CompleteActionsRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.CompleteActionsRequest;

            /**
             * Creates a CompleteActionsRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns CompleteActionsRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.CompleteActionsRequest;

            /**
             * Creates a plain object from a CompleteActionsRequest message. Also converts values to other types if specified.
             * @param message CompleteActionsRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.CompleteActionsRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this CompleteActionsRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for CompleteActionsRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a CompleteActionsResponse. */
        interface ICompleteActionsResponse {

            /** CompleteActionsResponse outcomes */
            outcomes?: (string[]|null);
        }

        /** Represents a CompleteActionsResponse. */
        class CompleteActionsResponse implements ICompleteActionsResponse {

            /**
             * Constructs a new CompleteActionsResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ICompleteActionsResponse);

            /** CompleteActionsResponse outcomes. */
            public outcomes: string[];

            /**
             * Creates a new CompleteActionsResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns CompleteActionsResponse instance
             */
            public static create(properties?: popclaw.world.ICompleteActionsResponse): popclaw.world.CompleteActionsResponse;

            /**
             * Encodes the specified CompleteActionsResponse message. Does not implicitly {@link popclaw.world.CompleteActionsResponse.verify|verify} messages.
             * @param message CompleteActionsResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ICompleteActionsResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a CompleteActionsResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns CompleteActionsResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.CompleteActionsResponse;

            /**
             * Creates a CompleteActionsResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns CompleteActionsResponse
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.CompleteActionsResponse;

            /**
             * Creates a plain object from a CompleteActionsResponse message. Also converts values to other types if specified.
             * @param message CompleteActionsResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.CompleteActionsResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this CompleteActionsResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for CompleteActionsResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ReadActionResultRequest. */
        interface IReadActionResultRequest {

            /** ReadActionResultRequest workerId */
            workerId?: (string|null);

            /** ReadActionResultRequest executionId */
            executionId?: (string|null);
        }

        /** Represents a ReadActionResultRequest. */
        class ReadActionResultRequest implements IReadActionResultRequest {

            /**
             * Constructs a new ReadActionResultRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IReadActionResultRequest);

            /** ReadActionResultRequest workerId. */
            public workerId: string;

            /** ReadActionResultRequest executionId. */
            public executionId: string;

            /**
             * Creates a new ReadActionResultRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ReadActionResultRequest instance
             */
            public static create(properties?: popclaw.world.IReadActionResultRequest): popclaw.world.ReadActionResultRequest;

            /**
             * Encodes the specified ReadActionResultRequest message. Does not implicitly {@link popclaw.world.ReadActionResultRequest.verify|verify} messages.
             * @param message ReadActionResultRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IReadActionResultRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ReadActionResultRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ReadActionResultRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ReadActionResultRequest;

            /**
             * Creates a ReadActionResultRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ReadActionResultRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ReadActionResultRequest;

            /**
             * Creates a plain object from a ReadActionResultRequest message. Also converts values to other types if specified.
             * @param message ReadActionResultRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ReadActionResultRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ReadActionResultRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ReadActionResultRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ReadActionResultResponse. */
        interface IReadActionResultResponse {

            /** ReadActionResultResponse result */
            result?: (popclaw.world.ISignedWorkerResult|null);
        }

        /** Represents a ReadActionResultResponse. */
        class ReadActionResultResponse implements IReadActionResultResponse {

            /**
             * Constructs a new ReadActionResultResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IReadActionResultResponse);

            /** ReadActionResultResponse result. */
            public result?: (popclaw.world.ISignedWorkerResult|null);

            /**
             * Creates a new ReadActionResultResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ReadActionResultResponse instance
             */
            public static create(properties?: popclaw.world.IReadActionResultResponse): popclaw.world.ReadActionResultResponse;

            /**
             * Encodes the specified ReadActionResultResponse message. Does not implicitly {@link popclaw.world.ReadActionResultResponse.verify|verify} messages.
             * @param message ReadActionResultResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IReadActionResultResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ReadActionResultResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ReadActionResultResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ReadActionResultResponse;

            /**
             * Creates a ReadActionResultResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ReadActionResultResponse
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ReadActionResultResponse;

            /**
             * Creates a plain object from a ReadActionResultResponse message. Also converts values to other types if specified.
             * @param message ReadActionResultResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ReadActionResultResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ReadActionResultResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ReadActionResultResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a RegisterPublicScopesRequest. */
        interface IRegisterPublicScopesRequest {

            /** RegisterPublicScopesRequest workerId */
            workerId?: (string|null);

            /** RegisterPublicScopesRequest house */
            house?: (popclaw.world.IHouseBinding|null);

            /** RegisterPublicScopesRequest scopeIds */
            scopeIds?: (string[]|null);
        }

        /** Represents a RegisterPublicScopesRequest. */
        class RegisterPublicScopesRequest implements IRegisterPublicScopesRequest {

            /**
             * Constructs a new RegisterPublicScopesRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IRegisterPublicScopesRequest);

            /** RegisterPublicScopesRequest workerId. */
            public workerId: string;

            /** RegisterPublicScopesRequest house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** RegisterPublicScopesRequest scopeIds. */
            public scopeIds: string[];

            /**
             * Creates a new RegisterPublicScopesRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns RegisterPublicScopesRequest instance
             */
            public static create(properties?: popclaw.world.IRegisterPublicScopesRequest): popclaw.world.RegisterPublicScopesRequest;

            /**
             * Encodes the specified RegisterPublicScopesRequest message. Does not implicitly {@link popclaw.world.RegisterPublicScopesRequest.verify|verify} messages.
             * @param message RegisterPublicScopesRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IRegisterPublicScopesRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a RegisterPublicScopesRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns RegisterPublicScopesRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.RegisterPublicScopesRequest;

            /**
             * Creates a RegisterPublicScopesRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns RegisterPublicScopesRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.RegisterPublicScopesRequest;

            /**
             * Creates a plain object from a RegisterPublicScopesRequest message. Also converts values to other types if specified.
             * @param message RegisterPublicScopesRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.RegisterPublicScopesRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this RegisterPublicScopesRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for RegisterPublicScopesRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a RegisterPublicScopesResponse. */
        interface IRegisterPublicScopesResponse {

            /** RegisterPublicScopesResponse registered */
            registered?: (string[]|null);
        }

        /** Represents a RegisterPublicScopesResponse. */
        class RegisterPublicScopesResponse implements IRegisterPublicScopesResponse {

            /**
             * Constructs a new RegisterPublicScopesResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IRegisterPublicScopesResponse);

            /** RegisterPublicScopesResponse registered. */
            public registered: string[];

            /**
             * Creates a new RegisterPublicScopesResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns RegisterPublicScopesResponse instance
             */
            public static create(properties?: popclaw.world.IRegisterPublicScopesResponse): popclaw.world.RegisterPublicScopesResponse;

            /**
             * Encodes the specified RegisterPublicScopesResponse message. Does not implicitly {@link popclaw.world.RegisterPublicScopesResponse.verify|verify} messages.
             * @param message RegisterPublicScopesResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IRegisterPublicScopesResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a RegisterPublicScopesResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns RegisterPublicScopesResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.RegisterPublicScopesResponse;

            /**
             * Creates a RegisterPublicScopesResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns RegisterPublicScopesResponse
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.RegisterPublicScopesResponse;

            /**
             * Creates a plain object from a RegisterPublicScopesResponse message. Also converts values to other types if specified.
             * @param message RegisterPublicScopesResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.RegisterPublicScopesResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this RegisterPublicScopesResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for RegisterPublicScopesResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a PublicationStatusRequest. */
        interface IPublicationStatusRequest {

            /** PublicationStatusRequest workerId */
            workerId?: (string|null);

            /** PublicationStatusRequest eventIds */
            eventIds?: (string[]|null);
        }

        /** Represents a PublicationStatusRequest. */
        class PublicationStatusRequest implements IPublicationStatusRequest {

            /**
             * Constructs a new PublicationStatusRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IPublicationStatusRequest);

            /** PublicationStatusRequest workerId. */
            public workerId: string;

            /** PublicationStatusRequest eventIds. */
            public eventIds: string[];

            /**
             * Creates a new PublicationStatusRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PublicationStatusRequest instance
             */
            public static create(properties?: popclaw.world.IPublicationStatusRequest): popclaw.world.PublicationStatusRequest;

            /**
             * Encodes the specified PublicationStatusRequest message. Does not implicitly {@link popclaw.world.PublicationStatusRequest.verify|verify} messages.
             * @param message PublicationStatusRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IPublicationStatusRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PublicationStatusRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PublicationStatusRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.PublicationStatusRequest;

            /**
             * Creates a PublicationStatusRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PublicationStatusRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.PublicationStatusRequest;

            /**
             * Creates a plain object from a PublicationStatusRequest message. Also converts values to other types if specified.
             * @param message PublicationStatusRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.PublicationStatusRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PublicationStatusRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PublicationStatusRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a PublicationStatusResponse. */
        interface IPublicationStatusResponse {

            /** PublicationStatusResponse receipts */
            receipts?: (popclaw.world.IPublicationReceipt[]|null);
        }

        /** Represents a PublicationStatusResponse. */
        class PublicationStatusResponse implements IPublicationStatusResponse {

            /**
             * Constructs a new PublicationStatusResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IPublicationStatusResponse);

            /** PublicationStatusResponse receipts. */
            public receipts: popclaw.world.IPublicationReceipt[];

            /**
             * Creates a new PublicationStatusResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PublicationStatusResponse instance
             */
            public static create(properties?: popclaw.world.IPublicationStatusResponse): popclaw.world.PublicationStatusResponse;

            /**
             * Encodes the specified PublicationStatusResponse message. Does not implicitly {@link popclaw.world.PublicationStatusResponse.verify|verify} messages.
             * @param message PublicationStatusResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IPublicationStatusResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PublicationStatusResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PublicationStatusResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.PublicationStatusResponse;

            /**
             * Creates a PublicationStatusResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PublicationStatusResponse
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.PublicationStatusResponse;

            /**
             * Creates a plain object from a PublicationStatusResponse message. Also converts values to other types if specified.
             * @param message PublicationStatusResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.PublicationStatusResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PublicationStatusResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PublicationStatusResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a RegisterBarrierRequest. */
        interface IRegisterBarrierRequest {

            /** RegisterBarrierRequest workerId */
            workerId?: (string|null);

            /** RegisterBarrierRequest barrier */
            barrier?: (popclaw.world.ISubscriptionBarrier|null);

            /** RegisterBarrierRequest registrationPage */
            registrationPage?: (number|null);

            /** RegisterBarrierRequest membersPage */
            membersPage?: (popclaw.world.IBarrierMember[]|null);
        }

        /** Represents a RegisterBarrierRequest. */
        class RegisterBarrierRequest implements IRegisterBarrierRequest {

            /**
             * Constructs a new RegisterBarrierRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IRegisterBarrierRequest);

            /** RegisterBarrierRequest workerId. */
            public workerId: string;

            /** RegisterBarrierRequest barrier. */
            public barrier?: (popclaw.world.ISubscriptionBarrier|null);

            /** RegisterBarrierRequest registrationPage. */
            public registrationPage: number;

            /** RegisterBarrierRequest membersPage. */
            public membersPage: popclaw.world.IBarrierMember[];

            /**
             * Creates a new RegisterBarrierRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns RegisterBarrierRequest instance
             */
            public static create(properties?: popclaw.world.IRegisterBarrierRequest): popclaw.world.RegisterBarrierRequest;

            /**
             * Encodes the specified RegisterBarrierRequest message. Does not implicitly {@link popclaw.world.RegisterBarrierRequest.verify|verify} messages.
             * @param message RegisterBarrierRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IRegisterBarrierRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a RegisterBarrierRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns RegisterBarrierRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.RegisterBarrierRequest;

            /**
             * Creates a RegisterBarrierRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns RegisterBarrierRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.RegisterBarrierRequest;

            /**
             * Creates a plain object from a RegisterBarrierRequest message. Also converts values to other types if specified.
             * @param message RegisterBarrierRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.RegisterBarrierRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this RegisterBarrierRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for RegisterBarrierRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a RegisterBarrierResponse. */
        interface IRegisterBarrierResponse {

            /** RegisterBarrierResponse barrierId */
            barrierId?: (string|null);

            /** RegisterBarrierResponse membersDigest */
            membersDigest?: (string|null);

            /** RegisterBarrierResponse membersReceived */
            membersReceived?: (number|Long|null);

            /** RegisterBarrierResponse memberTotal */
            memberTotal?: (number|Long|null);

            /** RegisterBarrierResponse registrationState */
            registrationState?: (string|null);
        }

        /** Represents a RegisterBarrierResponse. */
        class RegisterBarrierResponse implements IRegisterBarrierResponse {

            /**
             * Constructs a new RegisterBarrierResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IRegisterBarrierResponse);

            /** RegisterBarrierResponse barrierId. */
            public barrierId: string;

            /** RegisterBarrierResponse membersDigest. */
            public membersDigest: string;

            /** RegisterBarrierResponse membersReceived. */
            public membersReceived: (number|Long);

            /** RegisterBarrierResponse memberTotal. */
            public memberTotal: (number|Long);

            /** RegisterBarrierResponse registrationState. */
            public registrationState: string;

            /**
             * Creates a new RegisterBarrierResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns RegisterBarrierResponse instance
             */
            public static create(properties?: popclaw.world.IRegisterBarrierResponse): popclaw.world.RegisterBarrierResponse;

            /**
             * Encodes the specified RegisterBarrierResponse message. Does not implicitly {@link popclaw.world.RegisterBarrierResponse.verify|verify} messages.
             * @param message RegisterBarrierResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IRegisterBarrierResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a RegisterBarrierResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns RegisterBarrierResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.RegisterBarrierResponse;

            /**
             * Creates a RegisterBarrierResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns RegisterBarrierResponse
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.RegisterBarrierResponse;

            /**
             * Creates a plain object from a RegisterBarrierResponse message. Also converts values to other types if specified.
             * @param message RegisterBarrierResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.RegisterBarrierResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this RegisterBarrierResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for RegisterBarrierResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a CompleteBarrierRequest. */
        interface ICompleteBarrierRequest {

            /** CompleteBarrierRequest workerId */
            workerId?: (string|null);

            /** CompleteBarrierRequest barrierId */
            barrierId?: (string|null);

            /** CompleteBarrierRequest receipts */
            receipts?: (popclaw.world.IPublicationReceipt[]|null);
        }

        /** Represents a CompleteBarrierRequest. */
        class CompleteBarrierRequest implements ICompleteBarrierRequest {

            /**
             * Constructs a new CompleteBarrierRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ICompleteBarrierRequest);

            /** CompleteBarrierRequest workerId. */
            public workerId: string;

            /** CompleteBarrierRequest barrierId. */
            public barrierId: string;

            /** CompleteBarrierRequest receipts. */
            public receipts: popclaw.world.IPublicationReceipt[];

            /**
             * Creates a new CompleteBarrierRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns CompleteBarrierRequest instance
             */
            public static create(properties?: popclaw.world.ICompleteBarrierRequest): popclaw.world.CompleteBarrierRequest;

            /**
             * Encodes the specified CompleteBarrierRequest message. Does not implicitly {@link popclaw.world.CompleteBarrierRequest.verify|verify} messages.
             * @param message CompleteBarrierRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ICompleteBarrierRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a CompleteBarrierRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns CompleteBarrierRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.CompleteBarrierRequest;

            /**
             * Creates a CompleteBarrierRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns CompleteBarrierRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.CompleteBarrierRequest;

            /**
             * Creates a plain object from a CompleteBarrierRequest message. Also converts values to other types if specified.
             * @param message CompleteBarrierRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.CompleteBarrierRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this CompleteBarrierRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for CompleteBarrierRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a CompleteBarrierResponse. */
        interface ICompleteBarrierResponse {

            /** CompleteBarrierResponse readiness */
            readiness?: (popclaw.world.ISubscriptionReadiness|null);
        }

        /** Represents a CompleteBarrierResponse. */
        class CompleteBarrierResponse implements ICompleteBarrierResponse {

            /**
             * Constructs a new CompleteBarrierResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ICompleteBarrierResponse);

            /** CompleteBarrierResponse readiness. */
            public readiness?: (popclaw.world.ISubscriptionReadiness|null);

            /**
             * Creates a new CompleteBarrierResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns CompleteBarrierResponse instance
             */
            public static create(properties?: popclaw.world.ICompleteBarrierResponse): popclaw.world.CompleteBarrierResponse;

            /**
             * Encodes the specified CompleteBarrierResponse message. Does not implicitly {@link popclaw.world.CompleteBarrierResponse.verify|verify} messages.
             * @param message CompleteBarrierResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ICompleteBarrierResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a CompleteBarrierResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns CompleteBarrierResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.CompleteBarrierResponse;

            /**
             * Creates a CompleteBarrierResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns CompleteBarrierResponse
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.CompleteBarrierResponse;

            /**
             * Creates a plain object from a CompleteBarrierResponse message. Also converts values to other types if specified.
             * @param message CompleteBarrierResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.CompleteBarrierResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this CompleteBarrierResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for CompleteBarrierResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a CoveredSession. */
        interface ICoveredSession {

            /** CoveredSession sessionId */
            sessionId?: (string|null);

            /** CoveredSession enteredOpSeq */
            enteredOpSeq?: (number|Long|null);

            /** CoveredSession fence */
            fence?: (string|null);
        }

        /** Represents a CoveredSession. */
        class CoveredSession implements ICoveredSession {

            /**
             * Constructs a new CoveredSession.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.ICoveredSession);

            /** CoveredSession sessionId. */
            public sessionId: string;

            /** CoveredSession enteredOpSeq. */
            public enteredOpSeq: (number|Long);

            /** CoveredSession fence. */
            public fence: string;

            /**
             * Creates a new CoveredSession instance using the specified properties.
             * @param [properties] Properties to set
             * @returns CoveredSession instance
             */
            public static create(properties?: popclaw.world.ICoveredSession): popclaw.world.CoveredSession;

            /**
             * Encodes the specified CoveredSession message. Does not implicitly {@link popclaw.world.CoveredSession.verify|verify} messages.
             * @param message CoveredSession message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.ICoveredSession, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a CoveredSession message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns CoveredSession
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.CoveredSession;

            /**
             * Creates a CoveredSession message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns CoveredSession
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.CoveredSession;

            /**
             * Creates a plain object from a CoveredSession message. Also converts values to other types if specified.
             * @param message CoveredSession
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.CoveredSession, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this CoveredSession to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for CoveredSession
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ClosureRecord. */
        interface IClosureRecord {

            /** ClosureRecord requestId */
            requestId?: (string|null);

            /** ClosureRecord executionId */
            executionId?: (string|null);

            /** ClosureRecord sessionId */
            sessionId?: (string|null);

            /** ClosureRecord status */
            status?: (string|null);

            /** ClosureRecord resultDigest */
            resultDigest?: (string|null);
        }

        /** Represents a ClosureRecord. */
        class ClosureRecord implements IClosureRecord {

            /**
             * Constructs a new ClosureRecord.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IClosureRecord);

            /** ClosureRecord requestId. */
            public requestId: string;

            /** ClosureRecord executionId. */
            public executionId: string;

            /** ClosureRecord sessionId. */
            public sessionId: string;

            /** ClosureRecord status. */
            public status: string;

            /** ClosureRecord resultDigest. */
            public resultDigest: string;

            /**
             * Creates a new ClosureRecord instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ClosureRecord instance
             */
            public static create(properties?: popclaw.world.IClosureRecord): popclaw.world.ClosureRecord;

            /**
             * Encodes the specified ClosureRecord message. Does not implicitly {@link popclaw.world.ClosureRecord.verify|verify} messages.
             * @param message ClosureRecord message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IClosureRecord, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ClosureRecord message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ClosureRecord
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ClosureRecord;

            /**
             * Creates a ClosureRecord message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ClosureRecord
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ClosureRecord;

            /**
             * Creates a plain object from a ClosureRecord message. Also converts values to other types if specified.
             * @param message ClosureRecord
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ClosureRecord, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ClosureRecord to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ClosureRecord
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an ExecutionClosure. */
        interface IExecutionClosure {

            /** ExecutionClosure version */
            version?: (number|null);

            /** ExecutionClosure closureId */
            closureId?: (string|null);

            /** ExecutionClosure house */
            house?: (popclaw.world.IHouseBinding|null);

            /** ExecutionClosure actorId */
            actorId?: (string|null);

            /** ExecutionClosure installationId */
            installationId?: (string|null);

            /** ExecutionClosure stopRequestId */
            stopRequestId?: (string|null);

            /** ExecutionClosure stopThroughOpSeq */
            stopThroughOpSeq?: (number|Long|null);

            /** ExecutionClosure coveredSessions */
            coveredSessions?: (popclaw.world.ICoveredSession[]|null);

            /** ExecutionClosure coveredDigest */
            coveredDigest?: (string|null);

            /** ExecutionClosure pendingCount */
            pendingCount?: (number|Long|null);

            /** ExecutionClosure succeededCount */
            succeededCount?: (number|Long|null);

            /** ExecutionClosure rejectedCount */
            rejectedCount?: (number|Long|null);

            /** ExecutionClosure cancelledCount */
            cancelledCount?: (number|Long|null);

            /** ExecutionClosure resultsDigest */
            resultsDigest?: (string|null);

            /** ExecutionClosure phase */
            phase?: (string|null);
        }

        /** Represents an ExecutionClosure. */
        class ExecutionClosure implements IExecutionClosure {

            /**
             * Constructs a new ExecutionClosure.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IExecutionClosure);

            /** ExecutionClosure version. */
            public version: number;

            /** ExecutionClosure closureId. */
            public closureId: string;

            /** ExecutionClosure house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** ExecutionClosure actorId. */
            public actorId: string;

            /** ExecutionClosure installationId. */
            public installationId: string;

            /** ExecutionClosure stopRequestId. */
            public stopRequestId: string;

            /** ExecutionClosure stopThroughOpSeq. */
            public stopThroughOpSeq: (number|Long);

            /** ExecutionClosure coveredSessions. */
            public coveredSessions: popclaw.world.ICoveredSession[];

            /** ExecutionClosure coveredDigest. */
            public coveredDigest: string;

            /** ExecutionClosure pendingCount. */
            public pendingCount: (number|Long);

            /** ExecutionClosure succeededCount. */
            public succeededCount: (number|Long);

            /** ExecutionClosure rejectedCount. */
            public rejectedCount: (number|Long);

            /** ExecutionClosure cancelledCount. */
            public cancelledCount: (number|Long);

            /** ExecutionClosure resultsDigest. */
            public resultsDigest: string;

            /** ExecutionClosure phase. */
            public phase: string;

            /**
             * Creates a new ExecutionClosure instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ExecutionClosure instance
             */
            public static create(properties?: popclaw.world.IExecutionClosure): popclaw.world.ExecutionClosure;

            /**
             * Encodes the specified ExecutionClosure message. Does not implicitly {@link popclaw.world.ExecutionClosure.verify|verify} messages.
             * @param message ExecutionClosure message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IExecutionClosure, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an ExecutionClosure message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ExecutionClosure
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ExecutionClosure;

            /**
             * Creates an ExecutionClosure message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ExecutionClosure
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ExecutionClosure;

            /**
             * Creates a plain object from an ExecutionClosure message. Also converts values to other types if specified.
             * @param message ExecutionClosure
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ExecutionClosure, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ExecutionClosure to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ExecutionClosure
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** ClosureQueryResult enum. */
        enum ClosureQueryResult {
            CLOSURE_QUERY_UNSPECIFIED = 0,
            CLOSURE_NOT_FOUND = 1,
            CLOSURE_NOT_CREATED = 2,
            CLOSURE_CLOSING = 3,
            CLOSURE_CLOSED = 4,
            CLOSURE_INCARNATION_MISMATCH = 5
        }

        /** Properties of a ClosureQueryRequest. */
        interface IClosureQueryRequest {

            /** ClosureQueryRequest house */
            house?: (popclaw.world.IHouseBinding|null);

            /** ClosureQueryRequest actorId */
            actorId?: (string|null);

            /** ClosureQueryRequest installationId */
            installationId?: (string|null);

            /** ClosureQueryRequest stopRequestId */
            stopRequestId?: (string|null);

            /** ClosureQueryRequest stopThroughOpSeq */
            stopThroughOpSeq?: (number|Long|null);

            /** ClosureQueryRequest requestId */
            requestId?: (string|null);

            /** ClosureQueryRequest nonce */
            nonce?: (string|null);

            /** ClosureQueryRequest issuedAt */
            issuedAt?: (number|Long|null);

            /** ClosureQueryRequest expiresAt */
            expiresAt?: (number|Long|null);

            /** ClosureQueryRequest page */
            page?: (number|Long|null);

            /** ClosureQueryRequest signature */
            signature?: (Uint8Array|null);
        }

        /** Represents a ClosureQueryRequest. */
        class ClosureQueryRequest implements IClosureQueryRequest {

            /**
             * Constructs a new ClosureQueryRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IClosureQueryRequest);

            /** ClosureQueryRequest house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** ClosureQueryRequest actorId. */
            public actorId: string;

            /** ClosureQueryRequest installationId. */
            public installationId: string;

            /** ClosureQueryRequest stopRequestId. */
            public stopRequestId: string;

            /** ClosureQueryRequest stopThroughOpSeq. */
            public stopThroughOpSeq: (number|Long);

            /** ClosureQueryRequest requestId. */
            public requestId: string;

            /** ClosureQueryRequest nonce. */
            public nonce: string;

            /** ClosureQueryRequest issuedAt. */
            public issuedAt: (number|Long);

            /** ClosureQueryRequest expiresAt. */
            public expiresAt: (number|Long);

            /** ClosureQueryRequest page. */
            public page: (number|Long);

            /** ClosureQueryRequest signature. */
            public signature: Uint8Array;

            /**
             * Creates a new ClosureQueryRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ClosureQueryRequest instance
             */
            public static create(properties?: popclaw.world.IClosureQueryRequest): popclaw.world.ClosureQueryRequest;

            /**
             * Encodes the specified ClosureQueryRequest message. Does not implicitly {@link popclaw.world.ClosureQueryRequest.verify|verify} messages.
             * @param message ClosureQueryRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IClosureQueryRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ClosureQueryRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ClosureQueryRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ClosureQueryRequest;

            /**
             * Creates a ClosureQueryRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ClosureQueryRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ClosureQueryRequest;

            /**
             * Creates a plain object from a ClosureQueryRequest message. Also converts values to other types if specified.
             * @param message ClosureQueryRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ClosureQueryRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ClosureQueryRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ClosureQueryRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ClosureObservation. */
        interface IClosureObservation {

            /** ClosureObservation version */
            version?: (number|null);

            /** ClosureObservation house */
            house?: (popclaw.world.IHouseBinding|null);

            /** ClosureObservation actorId */
            actorId?: (string|null);

            /** ClosureObservation installationId */
            installationId?: (string|null);

            /** ClosureObservation closureId */
            closureId?: (string|null);

            /** ClosureObservation stopRequestId */
            stopRequestId?: (string|null);

            /** ClosureObservation stopThroughOpSeq */
            stopThroughOpSeq?: (number|Long|null);

            /** ClosureObservation queryRequestId */
            queryRequestId?: (string|null);

            /** ClosureObservation queryNonce */
            queryNonce?: (string|null);

            /** ClosureObservation observationRevision */
            observationRevision?: (number|Long|null);

            /** ClosureObservation observedAt */
            observedAt?: (number|Long|null);

            /** ClosureObservation result */
            result?: (popclaw.world.ClosureQueryResult|null);

            /** ClosureObservation closure */
            closure?: (popclaw.world.IExecutionClosure|null);

            /** ClosureObservation closureDigest */
            closureDigest?: (string|null);

            /** ClosureObservation recordsPageIndex */
            recordsPageIndex?: (number|Long|null);

            /** ClosureObservation recordsPage */
            recordsPage?: (popclaw.world.IClosureRecord[]|null);

            /** ClosureObservation signature */
            signature?: (Uint8Array|null);
        }

        /** Represents a ClosureObservation. */
        class ClosureObservation implements IClosureObservation {

            /**
             * Constructs a new ClosureObservation.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IClosureObservation);

            /** ClosureObservation version. */
            public version: number;

            /** ClosureObservation house. */
            public house?: (popclaw.world.IHouseBinding|null);

            /** ClosureObservation actorId. */
            public actorId: string;

            /** ClosureObservation installationId. */
            public installationId: string;

            /** ClosureObservation closureId. */
            public closureId: string;

            /** ClosureObservation stopRequestId. */
            public stopRequestId: string;

            /** ClosureObservation stopThroughOpSeq. */
            public stopThroughOpSeq: (number|Long);

            /** ClosureObservation queryRequestId. */
            public queryRequestId: string;

            /** ClosureObservation queryNonce. */
            public queryNonce: string;

            /** ClosureObservation observationRevision. */
            public observationRevision: (number|Long);

            /** ClosureObservation observedAt. */
            public observedAt: (number|Long);

            /** ClosureObservation result. */
            public result: popclaw.world.ClosureQueryResult;

            /** ClosureObservation closure. */
            public closure?: (popclaw.world.IExecutionClosure|null);

            /** ClosureObservation closureDigest. */
            public closureDigest: string;

            /** ClosureObservation recordsPageIndex. */
            public recordsPageIndex: (number|Long);

            /** ClosureObservation recordsPage. */
            public recordsPage: popclaw.world.IClosureRecord[];

            /** ClosureObservation signature. */
            public signature: Uint8Array;

            /**
             * Creates a new ClosureObservation instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ClosureObservation instance
             */
            public static create(properties?: popclaw.world.IClosureObservation): popclaw.world.ClosureObservation;

            /**
             * Encodes the specified ClosureObservation message. Does not implicitly {@link popclaw.world.ClosureObservation.verify|verify} messages.
             * @param message ClosureObservation message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IClosureObservation, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ClosureObservation message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ClosureObservation
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ClosureObservation;

            /**
             * Creates a ClosureObservation message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ClosureObservation
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ClosureObservation;

            /**
             * Creates a plain object from a ClosureObservation message. Also converts values to other types if specified.
             * @param message ClosureObservation
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ClosureObservation, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ClosureObservation to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ClosureObservation
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a ClosureQueryResponse. */
        interface IClosureQueryResponse {

            /** ClosureQueryResponse result */
            result?: (popclaw.world.ClosureQueryResult|null);

            /** ClosureQueryResponse observation */
            observation?: (popclaw.world.IClosureObservation|null);

            /** ClosureQueryResponse currentHouse */
            currentHouse?: (popclaw.world.IHouseBinding|null);

            /** ClosureQueryResponse detailCode */
            detailCode?: (string|null);
        }

        /** Represents a ClosureQueryResponse. */
        class ClosureQueryResponse implements IClosureQueryResponse {

            /**
             * Constructs a new ClosureQueryResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IClosureQueryResponse);

            /** ClosureQueryResponse result. */
            public result: popclaw.world.ClosureQueryResult;

            /** ClosureQueryResponse observation. */
            public observation?: (popclaw.world.IClosureObservation|null);

            /** ClosureQueryResponse currentHouse. */
            public currentHouse?: (popclaw.world.IHouseBinding|null);

            /** ClosureQueryResponse detailCode. */
            public detailCode: string;

            /**
             * Creates a new ClosureQueryResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ClosureQueryResponse instance
             */
            public static create(properties?: popclaw.world.IClosureQueryResponse): popclaw.world.ClosureQueryResponse;

            /**
             * Encodes the specified ClosureQueryResponse message. Does not implicitly {@link popclaw.world.ClosureQueryResponse.verify|verify} messages.
             * @param message ClosureQueryResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IClosureQueryResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ClosureQueryResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ClosureQueryResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.ClosureQueryResponse;

            /**
             * Creates a ClosureQueryResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ClosureQueryResponse
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.ClosureQueryResponse;

            /**
             * Creates a plain object from a ClosureQueryResponse message. Also converts values to other types if specified.
             * @param message ClosureQueryResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.ClosureQueryResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ClosureQueryResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ClosureQueryResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a PublicStreamBoundary. */
        interface IPublicStreamBoundary {

            /** PublicStreamBoundary logIncarnation */
            logIncarnation?: (string|null);

            /** PublicStreamBoundary scopes */
            scopes?: (string[]|null);

            /** PublicStreamBoundary highWaterSeq */
            highWaterSeq?: (number|Long|null);

            /** PublicStreamBoundary fullPublic */
            fullPublic?: (boolean|null);
        }

        /** Represents a PublicStreamBoundary. */
        class PublicStreamBoundary implements IPublicStreamBoundary {

            /**
             * Constructs a new PublicStreamBoundary.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IPublicStreamBoundary);

            /** PublicStreamBoundary logIncarnation. */
            public logIncarnation: string;

            /** PublicStreamBoundary scopes. */
            public scopes: string[];

            /** PublicStreamBoundary highWaterSeq. */
            public highWaterSeq: (number|Long);

            /** PublicStreamBoundary fullPublic. */
            public fullPublic: boolean;

            /**
             * Creates a new PublicStreamBoundary instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PublicStreamBoundary instance
             */
            public static create(properties?: popclaw.world.IPublicStreamBoundary): popclaw.world.PublicStreamBoundary;

            /**
             * Encodes the specified PublicStreamBoundary message. Does not implicitly {@link popclaw.world.PublicStreamBoundary.verify|verify} messages.
             * @param message PublicStreamBoundary message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IPublicStreamBoundary, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PublicStreamBoundary message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PublicStreamBoundary
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.PublicStreamBoundary;

            /**
             * Creates a PublicStreamBoundary message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PublicStreamBoundary
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.PublicStreamBoundary;

            /**
             * Creates a plain object from a PublicStreamBoundary message. Also converts values to other types if specified.
             * @param message PublicStreamBoundary
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.PublicStreamBoundary, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PublicStreamBoundary to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PublicStreamBoundary
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a PublicStreamCheckpoint. */
        interface IPublicStreamCheckpoint {

            /** PublicStreamCheckpoint phase */
            phase?: (string|null);

            /** PublicStreamCheckpoint scopes */
            scopes?: (popclaw.world.IScopeThrough[]|null);

            /** PublicStreamCheckpoint publicThroughSeq */
            publicThroughSeq?: (number|Long|null);
        }

        /** Represents a PublicStreamCheckpoint. */
        class PublicStreamCheckpoint implements IPublicStreamCheckpoint {

            /**
             * Constructs a new PublicStreamCheckpoint.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IPublicStreamCheckpoint);

            /** PublicStreamCheckpoint phase. */
            public phase: string;

            /** PublicStreamCheckpoint scopes. */
            public scopes: popclaw.world.IScopeThrough[];

            /** PublicStreamCheckpoint publicThroughSeq. */
            public publicThroughSeq?: (number|Long|null);

            /** PublicStreamCheckpoint _publicThroughSeq. */
            public _publicThroughSeq?: "publicThroughSeq";

            /**
             * Creates a new PublicStreamCheckpoint instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PublicStreamCheckpoint instance
             */
            public static create(properties?: popclaw.world.IPublicStreamCheckpoint): popclaw.world.PublicStreamCheckpoint;

            /**
             * Encodes the specified PublicStreamCheckpoint message. Does not implicitly {@link popclaw.world.PublicStreamCheckpoint.verify|verify} messages.
             * @param message PublicStreamCheckpoint message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IPublicStreamCheckpoint, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PublicStreamCheckpoint message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PublicStreamCheckpoint
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.PublicStreamCheckpoint;

            /**
             * Creates a PublicStreamCheckpoint message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PublicStreamCheckpoint
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.PublicStreamCheckpoint;

            /**
             * Creates a plain object from a PublicStreamCheckpoint message. Also converts values to other types if specified.
             * @param message PublicStreamCheckpoint
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.PublicStreamCheckpoint, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PublicStreamCheckpoint to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PublicStreamCheckpoint
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a PublicStreamGap. */
        interface IPublicStreamGap {

            /** PublicStreamGap reason */
            reason?: (string|null);

            /** PublicStreamGap lane */
            lane?: (string|null);

            /** PublicStreamGap scopeId */
            scopeId?: (string|null);

            /** PublicStreamGap boundary */
            boundary?: (popclaw.world.IPublicStreamBoundary|null);
        }

        /** Represents a PublicStreamGap. */
        class PublicStreamGap implements IPublicStreamGap {

            /**
             * Constructs a new PublicStreamGap.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.world.IPublicStreamGap);

            /** PublicStreamGap reason. */
            public reason: string;

            /** PublicStreamGap lane. */
            public lane: string;

            /** PublicStreamGap scopeId. */
            public scopeId: string;

            /** PublicStreamGap boundary. */
            public boundary?: (popclaw.world.IPublicStreamBoundary|null);

            /**
             * Creates a new PublicStreamGap instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PublicStreamGap instance
             */
            public static create(properties?: popclaw.world.IPublicStreamGap): popclaw.world.PublicStreamGap;

            /**
             * Encodes the specified PublicStreamGap message. Does not implicitly {@link popclaw.world.PublicStreamGap.verify|verify} messages.
             * @param message PublicStreamGap message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.world.IPublicStreamGap, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PublicStreamGap message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PublicStreamGap
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.world.PublicStreamGap;

            /**
             * Creates a PublicStreamGap message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PublicStreamGap
             */
            public static fromObject(object: { [k: string]: any }): popclaw.world.PublicStreamGap;

            /**
             * Creates a plain object from a PublicStreamGap message. Also converts values to other types if specified.
             * @param message PublicStreamGap
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.world.PublicStreamGap, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PublicStreamGap to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PublicStreamGap
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }
    }

    /** Namespace housesession. */
    namespace housesession {

        /** Operation enum. */
        enum Operation {
            OPERATION_UNSPECIFIED = 0,
            ENTER = 1,
            RENEW = 2,
            LEAVE = 3,
            STATUS = 4,
            ACTION = 5
        }

        /** Outcome enum. */
        enum Outcome {
            OUTCOME_UNSPECIFIED = 0,
            ENTERED = 1,
            ALREADY_ENTERED = 2,
            RENEWED = 3,
            CLOSED = 4,
            ALREADY_CLOSED = 5,
            SUPERSEDED = 6,
            REJECTED = 7,
            REPORTED = 8,
            COMMITTED = 9
        }

        /** ErrorCode enum. */
        enum ErrorCode {
            ERROR_UNSPECIFIED = 0,
            INVALID_HOUSE = 1,
            HOUSE_LIFECYCLE_UNSUPPORTED = 2,
            HOUSE_DISABLED = 3,
            EXECUTOR_BUSY = 4,
            STALE_OPERATION = 5,
            SESSION_FENCED = 6,
            LEASE_EXPIRED = 7,
            AUTH_INVALID = 8,
            AUDIENCE_MISMATCH = 9,
            IDEMPOTENCY_CONFLICT = 10,
            PERSISTENCE_FAILED = 11,
            ACTION_RESULT_UNKNOWN = 12
        }

        /** Properties of a RequestCore. */
        interface IRequestCore {

            /** RequestCore operation */
            operation?: (popclaw.housesession.Operation|null);

            /** RequestCore popclawId */
            popclawId?: (string|null);

            /** RequestCore installationId */
            installationId?: (string|null);

            /** RequestCore opSeq */
            opSeq?: (number|Long|null);

            /** RequestCore requestId */
            requestId?: (string|null);

            /** RequestCore houseOrigin */
            houseOrigin?: (string|null);

            /** RequestCore issuedAt */
            issuedAt?: (number|Long|null);

            /** RequestCore expiresAt */
            expiresAt?: (number|Long|null);

            /** RequestCore nonce */
            nonce?: (string|null);

            /** RequestCore expectedHouseRevision */
            expectedHouseRevision?: (number|Long|null);

            /** RequestCore targetSessionId */
            targetSessionId?: (string|null);

            /** RequestCore actionId */
            actionId?: (string|null);

            /** RequestCore actionExpiresAt */
            actionExpiresAt?: (number|Long|null);
        }

        /** Represents a RequestCore. */
        class RequestCore implements IRequestCore {

            /**
             * Constructs a new RequestCore.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.housesession.IRequestCore);

            /** RequestCore operation. */
            public operation: popclaw.housesession.Operation;

            /** RequestCore popclawId. */
            public popclawId: string;

            /** RequestCore installationId. */
            public installationId: string;

            /** RequestCore opSeq. */
            public opSeq: (number|Long);

            /** RequestCore requestId. */
            public requestId: string;

            /** RequestCore houseOrigin. */
            public houseOrigin: string;

            /** RequestCore issuedAt. */
            public issuedAt: (number|Long);

            /** RequestCore expiresAt. */
            public expiresAt: (number|Long);

            /** RequestCore nonce. */
            public nonce: string;

            /** RequestCore expectedHouseRevision. */
            public expectedHouseRevision: (number|Long);

            /** RequestCore targetSessionId. */
            public targetSessionId: string;

            /** RequestCore actionId. */
            public actionId: string;

            /** RequestCore actionExpiresAt. */
            public actionExpiresAt: (number|Long);

            /**
             * Creates a new RequestCore instance using the specified properties.
             * @param [properties] Properties to set
             * @returns RequestCore instance
             */
            public static create(properties?: popclaw.housesession.IRequestCore): popclaw.housesession.RequestCore;

            /**
             * Encodes the specified RequestCore message. Does not implicitly {@link popclaw.housesession.RequestCore.verify|verify} messages.
             * @param message RequestCore message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.housesession.IRequestCore, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a RequestCore message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns RequestCore
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.housesession.RequestCore;

            /**
             * Creates a RequestCore message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns RequestCore
             */
            public static fromObject(object: { [k: string]: any }): popclaw.housesession.RequestCore;

            /**
             * Creates a plain object from a RequestCore message. Also converts values to other types if specified.
             * @param message RequestCore
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.housesession.RequestCore, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this RequestCore to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for RequestCore
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an HouseSessionRequest. */
        interface IHouseSessionRequest {

            /** HouseSessionRequest core */
            core?: (popclaw.housesession.IRequestCore|null);

            /** HouseSessionRequest signature */
            signature?: (Uint8Array|null);

            /** HouseSessionRequest signerPubkey */
            signerPubkey?: (Uint8Array|null);
        }

        /** Represents an HouseSessionRequest. */
        class HouseSessionRequest implements IHouseSessionRequest {

            /**
             * Constructs a new HouseSessionRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.housesession.IHouseSessionRequest);

            /** HouseSessionRequest core. */
            public core?: (popclaw.housesession.IRequestCore|null);

            /** HouseSessionRequest signature. */
            public signature: Uint8Array;

            /** HouseSessionRequest signerPubkey. */
            public signerPubkey: Uint8Array;

            /**
             * Creates a new HouseSessionRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns HouseSessionRequest instance
             */
            public static create(properties?: popclaw.housesession.IHouseSessionRequest): popclaw.housesession.HouseSessionRequest;

            /**
             * Encodes the specified HouseSessionRequest message. Does not implicitly {@link popclaw.housesession.HouseSessionRequest.verify|verify} messages.
             * @param message HouseSessionRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.housesession.IHouseSessionRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an HouseSessionRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns HouseSessionRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.housesession.HouseSessionRequest;

            /**
             * Creates an HouseSessionRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns HouseSessionRequest
             */
            public static fromObject(object: { [k: string]: any }): popclaw.housesession.HouseSessionRequest;

            /**
             * Creates a plain object from an HouseSessionRequest message. Also converts values to other types if specified.
             * @param message HouseSessionRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.housesession.HouseSessionRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this HouseSessionRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for HouseSessionRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SessionInfo. */
        interface ISessionInfo {

            /** SessionInfo sessionId */
            sessionId?: (string|null);

            /** SessionInfo houseRevision */
            houseRevision?: (number|Long|null);

            /** SessionInfo leaseExpiresAt */
            leaseExpiresAt?: (number|Long|null);

            /** SessionInfo installationId */
            installationId?: (string|null);

            /** SessionInfo enteredOpSeq */
            enteredOpSeq?: (number|Long|null);
        }

        /** Represents a SessionInfo. */
        class SessionInfo implements ISessionInfo {

            /**
             * Constructs a new SessionInfo.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.housesession.ISessionInfo);

            /** SessionInfo sessionId. */
            public sessionId: string;

            /** SessionInfo houseRevision. */
            public houseRevision: (number|Long);

            /** SessionInfo leaseExpiresAt. */
            public leaseExpiresAt: (number|Long);

            /** SessionInfo installationId. */
            public installationId: string;

            /** SessionInfo enteredOpSeq. */
            public enteredOpSeq: (number|Long);

            /**
             * Creates a new SessionInfo instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SessionInfo instance
             */
            public static create(properties?: popclaw.housesession.ISessionInfo): popclaw.housesession.SessionInfo;

            /**
             * Encodes the specified SessionInfo message. Does not implicitly {@link popclaw.housesession.SessionInfo.verify|verify} messages.
             * @param message SessionInfo message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.housesession.ISessionInfo, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SessionInfo message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SessionInfo
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.housesession.SessionInfo;

            /**
             * Creates a SessionInfo message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SessionInfo
             */
            public static fromObject(object: { [k: string]: any }): popclaw.housesession.SessionInfo;

            /**
             * Creates a plain object from a SessionInfo message. Also converts values to other types if specified.
             * @param message SessionInfo
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.housesession.SessionInfo, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SessionInfo to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SessionInfo
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AckCore. */
        interface IAckCore {

            /** AckCore houseOrigin */
            houseOrigin?: (string|null);

            /** AckCore popclawId */
            popclawId?: (string|null);

            /** AckCore installationId */
            installationId?: (string|null);

            /** AckCore requestId */
            requestId?: (string|null);

            /** AckCore opSeq */
            opSeq?: (number|Long|null);

            /** AckCore operation */
            operation?: (popclaw.housesession.Operation|null);

            /** AckCore outcome */
            outcome?: (popclaw.housesession.Outcome|null);

            /** AckCore errorCode */
            errorCode?: (popclaw.housesession.ErrorCode|null);

            /** AckCore houseRevision */
            houseRevision?: (number|Long|null);

            /** AckCore sessionId */
            sessionId?: (string|null);

            /** AckCore sessionActive */
            sessionActive?: (boolean|null);

            /** AckCore leaseExpiresAt */
            leaseExpiresAt?: (number|Long|null);

            /** AckCore serverCommittedAt */
            serverCommittedAt?: (number|Long|null);

            /** AckCore status */
            status?: (popclaw.housesession.ISessionInfo|null);

            /** AckCore detail */
            detail?: (string|null);

            /** AckCore inboxReadToken */
            inboxReadToken?: (string|null);
        }

        /** Represents an AckCore. */
        class AckCore implements IAckCore {

            /**
             * Constructs a new AckCore.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.housesession.IAckCore);

            /** AckCore houseOrigin. */
            public houseOrigin: string;

            /** AckCore popclawId. */
            public popclawId: string;

            /** AckCore installationId. */
            public installationId: string;

            /** AckCore requestId. */
            public requestId: string;

            /** AckCore opSeq. */
            public opSeq: (number|Long);

            /** AckCore operation. */
            public operation: popclaw.housesession.Operation;

            /** AckCore outcome. */
            public outcome: popclaw.housesession.Outcome;

            /** AckCore errorCode. */
            public errorCode: popclaw.housesession.ErrorCode;

            /** AckCore houseRevision. */
            public houseRevision: (number|Long);

            /** AckCore sessionId. */
            public sessionId: string;

            /** AckCore sessionActive. */
            public sessionActive: boolean;

            /** AckCore leaseExpiresAt. */
            public leaseExpiresAt: (number|Long);

            /** AckCore serverCommittedAt. */
            public serverCommittedAt: (number|Long);

            /** AckCore status. */
            public status?: (popclaw.housesession.ISessionInfo|null);

            /** AckCore detail. */
            public detail: string;

            /** AckCore inboxReadToken. */
            public inboxReadToken: string;

            /**
             * Creates a new AckCore instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AckCore instance
             */
            public static create(properties?: popclaw.housesession.IAckCore): popclaw.housesession.AckCore;

            /**
             * Encodes the specified AckCore message. Does not implicitly {@link popclaw.housesession.AckCore.verify|verify} messages.
             * @param message AckCore message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.housesession.IAckCore, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AckCore message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AckCore
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.housesession.AckCore;

            /**
             * Creates an AckCore message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AckCore
             */
            public static fromObject(object: { [k: string]: any }): popclaw.housesession.AckCore;

            /**
             * Creates a plain object from an AckCore message. Also converts values to other types if specified.
             * @param message AckCore
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.housesession.AckCore, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AckCore to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AckCore
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an HouseSessionAck. */
        interface IHouseSessionAck {

            /** HouseSessionAck core */
            core?: (popclaw.housesession.IAckCore|null);

            /** HouseSessionAck signature */
            signature?: (Uint8Array|null);

            /** HouseSessionAck signerPubkey */
            signerPubkey?: (Uint8Array|null);
        }

        /** Represents an HouseSessionAck. */
        class HouseSessionAck implements IHouseSessionAck {

            /**
             * Constructs a new HouseSessionAck.
             * @param [properties] Properties to set
             */
            constructor(properties?: popclaw.housesession.IHouseSessionAck);

            /** HouseSessionAck core. */
            public core?: (popclaw.housesession.IAckCore|null);

            /** HouseSessionAck signature. */
            public signature: Uint8Array;

            /** HouseSessionAck signerPubkey. */
            public signerPubkey: Uint8Array;

            /**
             * Creates a new HouseSessionAck instance using the specified properties.
             * @param [properties] Properties to set
             * @returns HouseSessionAck instance
             */
            public static create(properties?: popclaw.housesession.IHouseSessionAck): popclaw.housesession.HouseSessionAck;

            /**
             * Encodes the specified HouseSessionAck message. Does not implicitly {@link popclaw.housesession.HouseSessionAck.verify|verify} messages.
             * @param message HouseSessionAck message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: popclaw.housesession.IHouseSessionAck, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an HouseSessionAck message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns HouseSessionAck
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): popclaw.housesession.HouseSessionAck;

            /**
             * Creates an HouseSessionAck message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns HouseSessionAck
             */
            public static fromObject(object: { [k: string]: any }): popclaw.housesession.HouseSessionAck;

            /**
             * Creates a plain object from an HouseSessionAck message. Also converts values to other types if specified.
             * @param message HouseSessionAck
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: popclaw.housesession.HouseSessionAck, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this HouseSessionAck to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for HouseSessionAck
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }
    }
}
